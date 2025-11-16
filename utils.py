import os
import json
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def groq_chat(prompt: str, max_tokens: int = 512) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY in .env")
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0, "max_tokens": max_tokens}
    r = requests.post(url, headers=headers, json=payload, timeout=40)
    if r.status_code != 200:
        raise RuntimeError(f"GROQ API error {r.status_code}: {r.text}")
    return r.json()["choices"][0]["message"]["content"]

def extract_triples_with_groq(text: str) -> List[dict]:
    prompt = f"""Extract triples from the text. Return ONLY a JSON array like:\n[{{"sub":"A","rel":"works_at","obj":"B"}}]\n\nText:\n{text}\n\nJSON:"""
    try:
        raw = groq_chat(prompt, max_tokens=512)
        s = raw.find("["); e = raw.rfind("]") + 1
        arr = json.loads(raw[s:e])
        out = []
        for t in arr:
            if all(k in t for k in ("sub","rel","obj")):
                out.append({"sub": str(t["sub"]), "rel": str(t["rel"]), "obj": str(t["obj"])})
        return out
    except Exception:
        return []

def extract_entities_with_groq(question: str) -> List[str]:
    prompt = f"""Extract all entities (names, places, companies, dates) from the question below.\nReturn ONLY a JSON array of strings.\n\nQuestion: \"{question}\"\n\nJSON:"""
    try:
        raw = groq_chat(prompt, max_tokens=200)
        s = raw.find("["); e = raw.rfind("]") + 1
        arr = json.loads(raw[s:e])
        return [str(x).strip() for x in arr]
    except Exception:
        return []

def chunk_text(text: str, max_chars: int = 700):
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        next_dot = text.find(". ", end)
        if next_dot != -1 and next_dot - start < 1200:
            end = next_dot + 1
        chunks.append(text[start:end].strip())
        start = end
    return chunks
