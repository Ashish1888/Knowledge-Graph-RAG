📚 K-Graph RAG — Hybrid Knowledge Graph + Vector RAG (FastAPI + Groq Llama 3.3)

A fully working K-Graph RAG (Knowledge-Graph-Augmented Retrieval-Augmented Generation) system built using:

🧠 Knowledge Graph (NetworkX)

📦 Vector Store (FAISS / numpy fallback)

🔍 Chunk-based semantic retrieval

🔗 Triple extraction via LLM

🏗 Graph-informed multi-hop reasoning

🤖 Groq LLaMA 3.3-70B for entity extraction + generation

⚡ FastAPI backend, testable using Postman

This project stores all data locally in:

data/meta.json     # vector metadata for chunks
data/graph.json    # KG triples as JSON
data/faiss.index   # vector embeddings (if FAISS available)
data/emb.npy       # fallback embeddings (numpy)


✔ This is a clean, modular, production-style implementation of a K-Graph RAG pipeline.

⭐ Features
🔵 Knowledge Graph (KG)

Auto-extracted triples like:

Alice -works_at-> Microsoft
Microsoft -headquartered_in-> Redmond


Multi-hop graph traversal (hops=1/2/3)

🟢 Vector Store

SentenceTransformers embeddings

FAISS (fast) or numpy (fallback)

Stores all chunks + document metadata in JSON

🟣 LLM Logic (via Groq)

Triple extraction

Entity extraction

Final answer generation using KG + vector context

🔥 API Endpoints

POST /ingest — ingest documents, chunk them, embed them, extract triples

POST /query — hybrid KG + vector retrieval + optional generation

GET /health — check totals and system status

🟩 Pure backend — fully testable with Postman, cURL, or any frontend.
📂 Project Structure
/project-root
│
├── main.py                # FastAPI app (routes)
├── vector_store.py        # Vector storage + FAISS index
├── graph_store.py         # Knowledge graph storage
├── utils.py               # Groq client, triple/entity extraction, chunking
│
├── data/                  # Auto-created
│   ├── meta.json          # JSON metadata for chunks
│   ├── graph.json         # JSON KG triples
│   ├── faiss.index        # Vector index (FAISS)
│   └── emb.npy            # Embedding matrix (fallback)
│
├── .env                   # API keys + config
└── README.md              # Documentation

⚙️ Installation
1. Clone the repository
git clone https://github.com/your-repo/kgraph-rag.git
cd kgraph-rag

2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # mac / linux
venv\Scripts\activate      # windows

3. Install dependencies
pip install -r requirements.txt

4. Create .env

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

DATA_DIR=data
EMBED_MODEL=all-MiniLM-L6-v2

REQUIRE_API_KEY=false
API_KEY_HEADER=supersecret

🚀 Run the Server
uvicorn main:app --reload


FastAPI will start at:

http://localhost:8000


Interactive docs:

http://localhost:8000/docs

📥 Ingest Documents (POST /ingest)
Example Request (Postman / cURL)
{
  "documents": [
    {
      "id": "doc1",
      "text": "Alice works at Microsoft. Microsoft is headquartered in Redmond."
    },
    {
      "id": "doc2",
      "text": "Bob works at Google. Google is based in Mountain View."
    }
  ]
}

🔎 Query (POST /query)
{
  "question": "Where does Alice work and where is that company located?",
  "top_k": 5,
  "hops": 2,
  "use_generation": true
}

Response Example
{
    "question": "Where does Alice work and where is that company located?",
    "entities": ["Alice", "Microsoft"],
    "graph": [
        {"sub":"Alice","rel":"works_at","obj":"Microsoft"},
        {"sub":"Microsoft","rel":"headquartered_in","obj":"Redmond"}
    ],
    "retrieved": [
        {
            "score": 0.60,
            "doc_id": "doc1",
            "chunk_id": "doc1::chunk::0",
            "text": "Alice works at Microsoft..."
        }
    ],
    "answer": "Alice works at Microsoft and Microsoft is headquartered in Redmond."
}

🧠 How K-Graph RAG Works
✔ Step 1 — Ingestion

Split text into chunks

Generate embeddings → store in meta.json

Extract triples → store in graph.json

✔ Step 2 — Query

Extract entities from question (LLM)

Traverse knowledge graph (1–3 hops)

Retrieve top-k vector chunks

Combine KG + retrieved text → final answer

This gives better reasoning than vector-only RAG.