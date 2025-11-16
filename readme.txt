📚 K-Graph RAG — Hybrid Knowledge Graph + Vector RAG (FastAPI + Groq LLaMA 3.3)

A fully working K-Graph RAG (Knowledge-Graph-Augmented Retrieval-Augmented Generation) system that combines graph reasoning and semantic vector search.
Built with:

🧠 Knowledge Graph (NetworkX)

📦 Vector Store (FAISS / numpy fallback)

🔍 Chunk-based semantic retrieval

🔗 Triple extraction via LLM (Groq LLaMA 3.3)

🏗 Graph-informed multi-hop reasoning

⚡ FastAPI backend

📬 Fully testable using Postman / cURL

📂 Local Storage Files
data/meta.json     # vector metadata for chunks
data/graph.json    # KG triples as JSON
data/faiss.index   # vector embeddings (if FAISS installed)
data/emb.npy       # fallback embeddings using numpy


✔ The system is modular, fully local, and production-style.

⭐ Features
🔵 Knowledge Graph (KG)

Extracts triples automatically:

Alice -works_at-> Microsoft
Microsoft -headquartered_in-> Redmond


Supports multi-hop reasoning (hops=1/2/3)

🟢 Vector Store

Uses SentenceTransformers for embeddings

FAISS for high-speed vector search

JSON-based metadata for easy debugging

🟣 LLM Logic (Groq)

Triple extraction

Entity extraction

LLM answer generation using KG facts + retrieved chunks

🔥 API Endpoints

POST /ingest → document ingestion, chunking, embedding, triple extraction

POST /query → hybrid retrieval + optional answer generation

GET /health → system + data stats

📁 Project Structure
project-root/
│
├── main.py                # FastAPI app (routes)
├── vector_store.py        # Vector storage + FAISS index
├── graph_store.py         # Knowledge graph storage
├── utils.py               # Groq client, triple/entity extraction, chunking
│
├── data/                  # Auto-created at runtime
│   ├── meta.json          # JSON metadata for chunks
│   ├── graph.json         # JSON KG triples
│   ├── faiss.index        # FAISS vector index
│   └── emb.npy            # Fallback embedding matrix
│
├── requirements.txt
├── .gitignore
├── .env                   # API keys + config (never push to GitHub)
└── README.md

⚙️ Installation
1️⃣ Clone the repository
git clone https://github.com/your-repo/kgraph-rag.git
cd kgraph-rag

2️⃣ Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

🔧 Create .env

Make a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

DATA_DIR=data
EMBED_MODEL=all-MiniLM-L6-v2

REQUIRE_API_KEY=false
API_KEY_HEADER=supersecret


⚠ .env is included in .gitignore.

🚀 Run the Server
uvicorn main:app --reload


FastAPI runs at:

API Base: http://localhost:8000

Docs: http://localhost:8000/docs

📥 Ingest Documents (POST /ingest)
Example Request
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

What ingestion does:

Chunks text

Creates embeddings → stores in vector DB

Extracts triples → stores in graph.json

🔎 Query (POST /query)
Example Request
{
  "question": "Where does Alice work and where is that company located?",
  "top_k": 5,
  "hops": 2,
  "use_generation": true
}

Example Response
{
  "question": "Where does Alice work and where is that company located?",
  "entities": ["Alice", "Microsoft"],
  "graph": [
    {"sub": "Alice", "rel": "works_at", "obj": "Microsoft"},
    {"sub": "Microsoft", "rel": "headquartered_in", "obj": "Redmond"}
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

Split document into chunks

Generate embeddings

Store embeddings in FAISS / emb.npy

Extract triples (LLM)

Append triples to graph.json

✔ Step 2 — Query

Extract entities from question (LLM)

Traverse knowledge graph (1–3 hops)

Retrieve top-k vector chunks

Build final answer from KG facts + chunk retrieval

This combination provides more accuracy and explainability than vector-only RAG.
