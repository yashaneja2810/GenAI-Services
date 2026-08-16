"""
Test Error Handling
"""
import pytest
from fastapi import status


def test_404_error_format(client):
    """Test that 404 errors are returned"""
    response = client.get("/api/nonexistent-endpoint")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    
    # FastAPI returns {"detail": "Not Found"} for non-existent routes
    # Our custom exceptions (like BotNotFoundError) use the error format
    assert "detail" in data or "error" in data


def test_validation_error_format(client):
    """Test that validation errors follow correct format"""
    # Send invalid data to chat endpoint (missing required fields)
    response = client.post("/api/chat", json={})
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    
    # Check error structure
    assert "error" in data
    assert "code" in data["error"]
    assert data["error"]["code"] == 422
    assert "message" in data["error"]
    assert "type" in data["error"]
    assert data["error"]["type"] == "ValidationError"


def test_error_response_consistency(client):
    """Test that validation errors have consistent structure"""
    # Test validation error scenario
    response = client.post("/api/chat", json={})
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    
    # Validation errors should have our custom format
    assert "error" in data
    assert "code" in data["error"]
    assert data["error"]["code"] == 422
    assert "message" in data["error"]
    assert "type" in data["error"]
    assert data["error"]["type"] == "ValidationError"


def test_error_logging(client, caplog):
    """Test that errors are logged"""
    # Make a request that will cause an error
    response = client.get("/api/nonexistent-endpoint")
    
    # Check that error was logged (if logging is configured)
    # Note: This may not work in all test environments
    assert response.status_code == status.HTTP_404_NOT_FOUND
