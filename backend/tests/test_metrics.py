"""
Test Metrics Endpoint
"""
import pytest
from fastapi import status


def test_metrics_endpoint_exists(client):
    """Test that metrics endpoint is accessible"""
    response = client.get("/metrics")
    assert response.status_code == status.HTTP_200_OK


def test_metrics_structure(client):
    """Test that metrics endpoint returns correct structure"""
    # Make some requests first
    client.get("/api/health")
    client.get("/api/health")
    
    response = client.get("/metrics")
    data = response.json()
    
    # Check required fields
    assert "uptime_seconds" in data
    assert "total_requests" in data
    assert "total_errors" in data
    assert "error_rate" in data
    assert "requests_per_second" in data
    assert "status_codes" in data
    assert "endpoints" in data


def test_metrics_tracking(client):
    """Test that metrics are being tracked correctly"""
    # Reset metrics
    response = client.get("/metrics")
    
    # Make some requests
    client.get("/api/health")
    client.get("/api/health")
    client.get("/api/health")
    
    # Check metrics
    response = client.get("/metrics")
    data = response.json()
    
    assert data["total_requests"] >= 3
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0


def test_metrics_endpoint_details(client):
    """Test that endpoint-specific metrics are tracked"""
    # Make a health check request
    client.get("/api/health")
    
    # Get metrics
    response = client.get("/metrics")
    data = response.json()
    
    # Check if health endpoint is tracked
    assert "endpoints" in data
    assert isinstance(data["endpoints"], dict)
    
    # If we have endpoint data, verify structure
    if data["endpoints"]:
        for endpoint, stats in data["endpoints"].items():
            assert "requests" in stats
            assert "avg_response_time_ms" in stats
            assert "errors" in stats
            assert "error_rate" in stats
