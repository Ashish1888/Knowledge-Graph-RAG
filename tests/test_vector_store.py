import pytest
import os
import tempfile
import json
from vector_store import VectorStore


class TestVectorStore:
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def vector_store(self, temp_data_dir):
        """Initialize a VectorStore instance with temporary directory"""
        return VectorStore(data_dir=temp_data_dir)

    def test_initialization(self, vector_store):
        """Test VectorStore initialization"""
        assert vector_store is not None
        assert len(vector_store.meta) == 0

    def test_add_documents(self, vector_store):
        """Test adding documents to vector store"""
        docs = [
            {
                "doc_id": "doc1",
                "chunk_id": "chunk1",
                "text": "This is a test document.",
                "source": "test"
            }
        ]
        vector_store.add(docs)
        assert len(vector_store.meta) == 1

    def test_add_multiple_documents(self, vector_store):
        """Test adding multiple documents"""
        docs = [
            {
                "doc_id": f"doc{i}",
                "chunk_id": f"chunk{i}",
                "text": f"Document {i} content.",
                "source": "test"
            }
            for i in range(5)
        ]
        vector_store.add(docs)
        assert len(vector_store.meta) == 5

    def test_search(self, vector_store):
        """Test searching in vector store"""
        docs = [
            {
                "doc_id": "doc1",
                "chunk_id": "chunk1",
                "text": "The quick brown fox jumps over the lazy dog.",
                "source": "test"
            }
        ]
        vector_store.add(docs)
        results = vector_store.search("fox", k=1)
        assert len(results) > 0

    def test_info(self, vector_store):
        """Test info method"""
        info = vector_store.info()
        assert "chunks" in info or "docs" in info

    def test_persistence(self, temp_data_dir):
        """Test that data persists after initialization"""
        # First instance
        vs1 = VectorStore(data_dir=temp_data_dir)
        docs = [
            {
                "doc_id": "persist1",
                "chunk_id": "chunk1",
                "text": "Persistent data test.",
                "source": "test"
            }
        ]
        vs1.add(docs)

        # Second instance should load persisted data
        vs2 = VectorStore(data_dir=temp_data_dir)
        assert len(vs2.meta) > 0
