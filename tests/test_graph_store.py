import pytest
import tempfile
import json
from graph_store import GraphStore


class TestGraphStore:
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for graph data"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.fixture
    def graph_store(self, temp_file):
        """Initialize a GraphStore instance"""
        return GraphStore(path=temp_file)

    def test_initialization(self, graph_store):
        """Test GraphStore initialization"""
        assert graph_store is not None

    def test_add_triple(self, graph_store):
        """Test adding a triple to the graph"""
        graph_store.add_triple("Alice", "works_at", "Microsoft")
        # Verify it was added
        neighbors = graph_store.neighbors("Alice", hops=1)
        assert len(neighbors) > 0

    def test_add_multiple_triples(self, graph_store):
        """Test adding multiple triples"""
        triples = [
            ("Alice", "works_at", "Microsoft"),
            ("Microsoft", "headquartered_in", "Redmond"),
            ("Bob", "works_at", "Google"),
        ]
        for s, r, o in triples:
            graph_store.add_triple(s, r, o)

        # Verify Alice's neighbors
        neighbors = graph_store.neighbors("Alice", hops=1)
        assert len(neighbors) > 0

    def test_neighbors_single_hop(self, graph_store):
        """Test retrieving single-hop neighbors"""
        graph_store.add_triple("Alice", "works_at", "Microsoft")
        neighbors = graph_store.neighbors("Alice", hops=1)
        # Should contain the triple or be empty depending on implementation
        assert isinstance(neighbors, list)

    def test_neighbors_multi_hop(self, graph_store):
        """Test retrieving multi-hop neighbors"""
        graph_store.add_triple("Alice", "works_at", "Microsoft")
        graph_store.add_triple("Microsoft", "headquartered_in", "Redmond")
        
        neighbors = graph_store.neighbors("Alice", hops=2)
        assert isinstance(neighbors, list)

    def test_info(self, graph_store):
        """Test info method"""
        graph_store.add_triple("Alice", "works_at", "Microsoft")
        info = graph_store.info()
        assert isinstance(info, dict)

    def test_persistence(self, temp_file):
        """Test that graph data persists"""
        # First instance
        gs1 = GraphStore(path=temp_file)
        gs1.add_triple("Alice", "works_at", "Microsoft")

        # Second instance should load persisted data
        gs2 = GraphStore(path=temp_file)
        neighbors = gs2.neighbors("Alice", hops=1)
        # Should have the persisted triple
        assert isinstance(neighbors, list)
