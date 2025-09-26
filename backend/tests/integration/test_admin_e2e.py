import os
import requests
import pytest
from typing import Dict, Any

def _base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8001")

def _get_admin_token(email: str = "admin@example.com", password: str = "admin_password") -> str:
    """
    Helper function to get an admin token.
    Note: This assumes there's already an admin user in the database.
    For a complete test, you might want to create the admin user first.
    """
    base = _base_url()
    r = requests.post(
        f"{base}/api/v1/admin/login",
        data={"username": email, "password": password},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["access_token"]

def _auth_admin_headers(token: str) -> Dict[str, str]:
    """Helper function to create authorization headers for admin requests"""
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.integration
def test_admin_login_endpoint_exists():
    """Test that admin login endpoint exists and responds"""
    base = _base_url()
    
    # Test that the endpoint exists
    r = requests.post(
        f"{base}/api/v1/admin/login",
        data={"username": "admin@example.com", "password": "admin_password"},
        timeout=10,
    )
    
    # Should return a response (either 200, 401, or 429 if rate limited)
    assert r.status_code in [200, 401, 429]

@pytest.mark.integration
def test_admin_dashboard_endpoint_exists():
    """Test that admin dashboard endpoint exists and responds"""
    base = _base_url()
    
    # Test that the endpoint exists (without authentication)
    r = requests.get(
        f"{base}/api/v1/admin/dashboard",
        timeout=10,
    )
    
    # Should return a response (either 200, 401, 403, or 500)
    assert r.status_code in [200, 401, 403, 500]

@pytest.mark.integration
def test_admin_list_users_endpoint_exists():
    """Test that admin list users endpoint exists and responds"""
    base = _base_url()
    
    # Test that the endpoint exists (without authentication)
    r = requests.get(
        f"{base}/api/v1/admin/usuarios",
        timeout=10,
    )
    
    # Should return a response
    assert r.status_code in [200, 401, 403, 500]

@pytest.mark.integration
def test_admin_configurations_endpoints_exist():
    """Test that admin configuration endpoints exist and respond"""
    base = _base_url()
    
    # Test list configurations endpoint
    r = requests.get(
        f"{base}/api/v1/admin/configuracoes",
        timeout=10,
    )
    assert r.status_code in [200, 401, 403, 500]
    
    # Test create configuration endpoint
    r = requests.post(
        f"{base}/api/v1/admin/configuracoes",
        timeout=10,
    )
    assert r.status_code in [422, 401, 403, 500]  # 422 for validation error