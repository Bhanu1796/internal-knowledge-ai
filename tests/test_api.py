from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import QueryResponse, SourceLink

client = TestClient(app)

# ─── Shared mock response ─────────────────────────────────────────────────────

def mock_pipeline_response(**kwargs) -> QueryResponse:
    defaults = dict(
        question="What is the annual leave policy?",
        answer="Employees get 20 days of annual leave per year.",
        intent="POLICY_LOOKUP",
        has_answer=True,
        sources=[
            SourceLink(
                title="Annual Leave Policy",
                url="https://confluence.internal/pages/annual-leave-policy",
                source_file="annual-leave-policy.md",
                page=0,
                score=0.91,
            )
        ],
        processing_time_ms=1200,
    )
    return QueryResponse(**{**defaults, **kwargs})


# ─── GET /health ──────────────────────────────────────────────────────────────

@patch("app.api.routes.get_collection_count", return_value=35)
def test_health_endpoint(mock_count):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["vector_store_docs"] == 35


# ─── POST /query ──────────────────────────────────────────────────────────────

@patch("app.api.routes.run_pipeline")
def test_query_endpoint_valid(mock_run):
    mock_run.return_value = mock_pipeline_response()

    response = client.post("/query", json={"question": "What is the annual leave policy?"})
    assert response.status_code == 200
    data = response.json()

    assert data["question"] == "What is the annual leave policy?"
    assert "20 days" in data["answer"]
    assert data["intent"] == "POLICY_LOOKUP"
    assert data["has_answer"] is True
    assert len(data["sources"]) == 1
    assert data["sources"][0]["title"] == "Annual Leave Policy"


@patch("app.api.routes.run_pipeline")
def test_query_endpoint_no_results(mock_run):
    mock_run.return_value = mock_pipeline_response(
        answer="I could not find relevant information in the knowledge base for your query.",
        has_answer=False,
        sources=[],
        intent="UNKNOWN",
    )

    response = client.post("/query", json={"question": "What is the wifi password at Tokyo office?"})
    assert response.status_code == 200
    data = response.json()
    assert data["has_answer"] is False
    assert data["sources"] == []


def test_query_endpoint_empty_question():
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422


def test_query_endpoint_missing_question():
    response = client.post("/query", json={})
    assert response.status_code == 422


@patch("app.api.routes.run_pipeline")
def test_query_endpoint_custom_top_k(mock_run):
    mock_run.return_value = mock_pipeline_response()

    client.post("/query", json={"question": "Some question", "top_k": 10})
    mock_run.assert_called_once_with(question="Some question", top_k=10)


# ─── GET /documents ───────────────────────────────────────────────────────────

@patch("app.api.routes.get_vector_store")
def test_documents_endpoint(mock_store):
    mock_collection = MagicMock()
    mock_collection.count.return_value = 35
    mock_collection.get.return_value = {
        "metadatas": [
            {"source": "annual-leave-policy.md", "title": "Annual Leave Policy", "doc_url": "https://confluence.internal/pages/annual-leave-policy"},
            {"source": "annual-leave-policy.md", "title": "Annual Leave Policy", "doc_url": "https://confluence.internal/pages/annual-leave-policy"},
            {"source": "it-software-request.md", "title": "It Software Request", "doc_url": "https://confluence.internal/pages/it-software-request"},
        ]
    }
    mock_store.return_value._collection = mock_collection

    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()

    assert data["total_chunks"] == 35
    assert data["total_documents"] == 2
    titles = [d["title"] for d in data["documents"]]
    assert "Annual Leave Policy" in titles
    assert "It Software Request" in titles
