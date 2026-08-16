"""
Test Health Check Endpoint
"""
import pytest
from fastapi import status


def test_health_check_success(client):
    """Test that health check endpoint returns 200"""
    response = client.get("/api/health")
    
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data
    assert "version" in data
    
    # Check that all expected services are present
    services = data["services"]
    assert "api" in services
    assert "qdrant" in services
    assert "supabase" in services
    assert "groq" in services


def test_health_check_response_structure(client):
    """Test that health check has correct structure"""
    response = client.get("/api/health")
    data = response.json()
    
    # Verify top-level fields
    assert isinstance(data["status"], str)
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    # Verify each service has status
    for service_name, service_data in data["services"].items():
        assert "status" in service_data
        assert service_data["status"] in ["healthy", "unhealthy"]


def test_health_check_response_time(client):
    """Test that health check includes response time"""
    response = client.get("/api/health")
    data = response.json()
    
    assert "response_time_ms" in data
    assert isinstance(data["response_time_ms"], (int, float))
    assert data["response_time_ms"] > 0
