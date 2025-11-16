import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestHealth:
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "ok"

    def test_health_has_info(self):
        """Test that health endpoint returns vector and graph info"""
        response = client.get("/health")
        data = response.json()
        assert "vector_info" in data
        assert "graph_info" in data


class TestIngest:
    def test_ingest_requires_api_key_when_enabled(self):
        """Test that API key is enforced when REQUIRE_API_KEY is true"""
        # This test depends on REQUIRE_API_KEY environment variable
        pass

    def test_ingest_single_document(self):
        """Test ingesting a single document"""
        payload = {
            "documents": [
                {
                    "id": "test-doc-1",
                    "text": "This is a test document.",
                    "source": "test"
                }
            ]
        }
        response = client.post("/ingest", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "added_chunks" in data
        assert "triples_added" in data

    def test_ingest_multiple_documents(self):
        """Test ingesting multiple documents"""
        payload = {
            "documents": [
                {
                    "id": "doc-1",
                    "text": "Alice works at Microsoft.",
                    "source": "test"
                },
                {
                    "id": "doc-2",
                    "text": "Bob works at Google.",
                    "source": "test"
                }
            ]
        }
        response = client.post("/ingest", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["added_chunks"] >= 2


class TestQuery:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data before each test"""
        payload = {
            "documents": [
                {
                    "id": "setup-doc",
                    "text": "Alice works at Microsoft. Microsoft is headquartered in Redmond.",
                    "source": "test"
                }
            ]
        }
        client.post("/ingest", json=payload)

    def test_query_basic(self):
        """Test basic query without generation"""
        payload = {
            "question": "Where does Alice work?",
            "top_k": 5,
            "hops": 1,
            "use_generation": False
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "question" in data
        assert "entities" in data
        assert "graph" in data
        assert "retrieved" in data

    def test_query_with_generation(self):
        """Test query with generation enabled"""
        payload = {
            "question": "Where is Alice's company headquartered?",
            "top_k": 5,
            "hops": 2,
            "use_generation": True
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_query_different_hops(self):
        """Test query with different hop counts"""
        for hops in [1, 2, 3]:
            payload = {
                "question": "Test query",
                "top_k": 5,
                "hops": hops,
                "use_generation": False
            }
            response = client.post("/query", json=payload)
            assert response.status_code == 200
