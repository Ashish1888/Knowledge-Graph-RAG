import os
import uuid
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

from vector_store import VectorStore
from graph_store import GraphStore
from utils import chunk_text, groq_chat, extract_triples_with_groq, extract_entities_with_groq

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "data")
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "supersecret")

# ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI(title="K-Graph RAG - modular JSON stores")

VS = VectorStore(data_dir=DATA_DIR)
KG = GraphStore(path=os.path.join(DATA_DIR, "graph.json"))

def auth(x_api_key: str = Header(None)):
    if REQUIRE_API_KEY and x_api_key != API_KEY_HEADER:
        raise HTTPException(status_code=401, detail="Invalid API key")

class DocItem(BaseModel):
    id: Optional[str]
    text: str
    source: Optional[str] = None

class IngestRequest(BaseModel):
    documents: List[DocItem]

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    hops: int = 1
    use_generation: bool = True

@app.get("/health")
def health():
    return {
        "status": "ok",
        "vector_info": VS.info(),
        "graph_info": KG.info()
    }

@app.post("/ingest")
def ingest(req: IngestRequest, x_api_key: str = Header(None)):
    auth(x_api_key)
    docs_to_add = []
    triples = []

    for d in req.documents:
        doc_id = d.id or str(uuid.uuid4())
        src = d.source or doc_id
        chunks = chunk_text(d.text)
        for i, c in enumerate(chunks):
            chunk_id = f"{doc_id}::chunk::{i}"
            docs_to_add.append({"doc_id": doc_id, "chunk_id": chunk_id, "text": c, "source": src})
            # extract triples (LLM)
            tlist = extract_triples_with_groq(c)
            for t in tlist:
                # guard keys and store to KG
                s = t.get("sub"); r = t.get("rel"); o = t.get("obj")
                if s and r and o:
                    KG.add_triple(s, r, o, source=doc_id)
                    triples.append({"sub": s, "rel": r, "obj": o, "source": doc_id})

    # add docs to vector store (this persists meta.json and embeddings)
    VS.add(docs_to_add)

    return {"added_chunks": len(docs_to_add), "triples_added": len(triples), "vector_meta_count": len(VS.meta)}

@app.post("/query")
def query(req: QueryRequest, x_api_key: str = Header(None)):
    auth(x_api_key)
    q = req.question

    # run entity extraction (LLM-backed)
    ents = extract_entities_with_groq(q)

    # match entities to nodes (case-insensitive) and do graph traversal
    graph_facts = []
    for e in ents:
        graph_facts.extend(KG.neighbors(e, hops=req.hops))

    # vector retrieval (DB-first can be added later)
    results = VS.search(q, req.top_k) if req.top_k > 0 else []
    retrieved_texts = [r["text"] for r in results]

    # build context with graph first
    ctx = ""
    if graph_facts:
        ctx += "GRAPH FACTS:\n" + "\n".join([f"{f['sub']} -{f['rel']}-> {f['obj']}" for f in graph_facts]) + "\n\n"
    if retrieved_texts:
        ctx += "RETRIEVED CHUNKS:\n" + "\n\n".join(retrieved_texts)

    answer = "Generation disabled."
    if req.use_generation:
        prompt = f"Use only the knowledge below to answer the question. Cite sources where possible.\n\n{ctx}\nQuestion: {q}\nAnswer concisely:"
        try:
            answer = groq_chat(prompt, max_tokens=512)
        except Exception as e:
            answer = f"Generation failed: {str(e)}"

    return {"question": q, "entities": ents, "graph": graph_facts, "retrieved": results, "answer": answer}
