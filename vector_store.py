import os
import json
import pathlib
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer

# feature flags
_HAS_FAISS = True
try:
    import faiss
except Exception:
    _HAS_FAISS = False
    from sklearn.metrics.pairwise import cosine_similarity  # fallback

MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

class VectorStore:
    def __init__(self, data_dir: str = "data", model_name: str = MODEL_NAME):
        pathlib.Path(data_dir).mkdir(parents=True, exist_ok=True)
        self.data_dir = data_dir
        self.meta_path = os.path.join(data_dir, "meta.json")
        self.emb_path = os.path.join(data_dir, "emb.npy")
        self.index_path = os.path.join(data_dir, "faiss.index")
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

        # load meta json (list of dicts)
        if os.path.exists(self.meta_path):
            self.meta: List[Dict[str, Any]] = json.load(open(self.meta_path, "r", encoding="utf-8"))
        else:
            self.meta = []
            self._save_meta()

        # load embeddings or faiss index
        if _HAS_FAISS:
            if os.path.exists(self.index_path):
                try:
                    self.index = faiss.read_index(self.index_path)
                except Exception:
                    self.index = faiss.IndexFlatL2(self.dim)
            else:
                self.index = faiss.IndexFlatL2(self.dim)
        else:
            if os.path.exists(self.emb_path):
                self.emb = np.load(self.emb_path)
            else:
                self.emb = np.zeros((0, self.dim), dtype="float32")

    def _save_meta(self):
        # atomic write
        tmp = self.meta_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.meta_path)

    def _save_index(self):
        if _HAS_FAISS:
            faiss.write_index(self.index, self.index_path)
        else:
            np.save(self.emb_path, self.emb)

    def save(self):
        self._save_index()
        self._save_meta()

    def _meta_has_chunk(self, chunk_id: str) -> bool:
        return any(m.get("chunk_id") == chunk_id for m in self.meta)

    def add(self, docs: List[Dict[str, Any]]):
        """
        docs: list of {"doc_id":..., "chunk_id":..., "text":..., "source":...}
        """
        if not docs:
            return
        # filter duplicates by chunk_id
        new_docs = [d for d in docs if not self._meta_has_chunk(d["chunk_id"])]
        if not new_docs:
            return

        texts = [d["text"] for d in new_docs]
        embs = self.model.encode(texts, convert_to_numpy=True).astype("float32")

        if _HAS_FAISS:
            self.index.add(embs)
        else:
            if self.emb.shape[0] == 0:
                self.emb = embs
            else:
                self.emb = np.vstack([self.emb, embs])

        # append metadata aligned with embeddings
        self.meta.extend(new_docs)
        self.save()

    def search(self, query: str, top_k: int = 5):
        # return list of {"score":..., "doc_id":..., "chunk_id":..., "text":...}
        if _HAS_FAISS:
            if self.index.ntotal == 0:
                return []
        else:
            if self.emb.shape[0] == 0:
                return []

        q_emb = self.model.encode([query], convert_to_numpy=True).astype("float32")

        if _HAS_FAISS:
            distances, indices = self.index.search(q_emb, top_k)
            out = []
            for d, i in zip(distances[0], indices[0]):
                if i < 0 or i >= len(self.meta):
                    continue
                meta = self.meta[i]
                out.append({"score": float(d), **meta})
            return out
        else:
            sims = cosine_similarity(q_emb, self.emb)[0]
            idxs = list(np.argsort(-sims)[:top_k])
            out = []
            for i in idxs:
                out.append({"score": float(1 - sims[i]), **self.meta[i]})
            return out

    def info(self):
        count = self.index.ntotal if _HAS_FAISS else (self.emb.shape[0] if hasattr(self, "emb") else 0)
        return {"ntotal": int(count), "meta_count": len(self.meta)}
