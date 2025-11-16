import os
import json
import pathlib
import networkx as nx
from typing import List, Dict, Any

class GraphStore:
    def __init__(self, path: str = "data/graph.json"):
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        if os.path.exists(self.path):
            try:
                raw = json.load(open(self.path, "r", encoding="utf-8"))
                self.G = nx.node_link_graph(raw)
            except Exception:
                self.G = nx.DiGraph()
        else:
            self.G = nx.DiGraph()
            self._save()

    def _save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(nx.node_link_data(self.G), f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def add_triple(self, s: str, r: str, o: str, source: str = None):
        # normalize simple string keys
        s = str(s).strip()
        o = str(o).strip()
        r = str(r).strip()
        if s not in self.G:
            self.G.add_node(s)
        if o not in self.G:
            self.G.add_node(o)
        # add edge with relation and optional source
        self.G.add_edge(s, o, rel=r, source=source)
        self._save()

    def neighbors(self, entity: str, hops: int = 1) -> List[Dict[str, Any]]:
        entity_lookup = None
        # case-insensitive node match
        lower = entity.lower()
        for n in self.G.nodes:
            if n.lower() == lower:
                entity_lookup = n
                break
        if entity_lookup is None:
            # also allow substring match
            for n in self.G.nodes:
                if n.lower() in lower or lower in n.lower():
                    entity_lookup = n
                    break
        if entity_lookup is None:
            return []
        frontier = {entity_lookup}
        results = set()
        for _ in range(hops):
            new = set()
            for n in frontier:
                for succ in self.G.successors(n):
                    rel = self.G.edges[n, succ].get("rel")
                    results.add((n, rel, succ))
                    new.add(succ)
                for pred in self.G.predecessors(n):
                    rel = self.G.edges[pred, n].get("rel")
                    results.add((pred, rel, n))
                    new.add(pred)
            frontier = new
        return [{"sub": s, "rel": r, "obj": o} for (s, r, o) in results]

    def info(self):
        return {"nodes": self.G.number_of_nodes(), "edges": self.G.number_of_edges()}
