"""
Pytest Configuration and Fixtures
Shared test setup and utilities
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.monitoring import metrics_collector


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_bot_id():
    """Sample bot ID for testing"""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing"""
    return "660e8400-e29b-41d4-a716-446655440001"


@pytest.fixture
def sample_document_content():
    """Sample document content for testing"""
    return """
    This is a sample document for testing purposes.
    It contains information about our products and services.
    Our company provides AI-powered chatbot solutions.
    Contact us at support@example.com for more information.
    """


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for authentication testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NjBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDEiLCJleHAiOjk5OTk5OTk5OTl9.test"


@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset metrics before each test"""
    metrics_collector.reset_metrics()
    yield
    metrics_collector.reset_metrics()


@pytest.fixture
def mock_qdrant_response():
    """Mock Qdrant search response"""
    return [
        {
            "text": "This is a test document chunk.",
            "score": 0.85,
            "metadata": {"filename": "test.pdf", "chunk_index": 0}
        },
        {
            "text": "Another relevant chunk of information.",
            "score": 0.75,
            "metadata": {"filename": "test.pdf", "chunk_index": 1}
        }
    ]


@pytest.fixture
def mock_groq_response():
    """Mock Groq API response"""
    return "This is a mock AI response based on the provided context."
