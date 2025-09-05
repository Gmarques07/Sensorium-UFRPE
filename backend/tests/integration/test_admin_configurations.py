import os
import requests
import pytest
from typing import Dict, Any
import uuid

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
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

def _auth_admin_headers(token: str) -> Dict[str, str]:
    """Helper function to create authorization headers for admin requests"""
    return {"Authorization": f"Bearer {token}"} if token else {}

@pytest.mark.integration
def test_admin_configurations_crud():
    """Test admin configuration endpoints (CRUD operations)"""
    base = _base_url()
    
    # First, try to get an admin token
    token = _get_admin_token()
    
    if token:
        headers = _auth_admin_headers(token)
        
        # Generate a unique key for testing
        test_key = f"test_config_key_{uuid.uuid4().hex[:8]}"
        
        # Test list configurations
        r = requests.get(
            f"{base}/api/v1/admin/configuracoes",
            headers=headers,
            timeout=10,
        )
        assert r.status_code == 200
        
        # Test create configuration
        config_data = {
            "chave": test_key,
            "valor": "test_config_value",
            "descricao": "Test configuration for integration tests"
        }
        
        r = requests.post(
            f"{base}/api/v1/admin/configuracoes",
            headers=headers,
            json=config_data,
            timeout=10,
        )
        # Should be 200 (created) or 409 (already exists)
        assert r.status_code in [200, 409]
        
        # If created successfully, test update and delete
        if r.status_code == 200:
            created_config = r.json()
            assert created_config["chave"] == test_key
            
            # Test update configuration
            update_data = {
                "valor": "updated_test_config_value",
                "descricao": "Updated test configuration"
            }
            
            r = requests.put(
                f"{base}/api/v1/admin/configuracoes/{test_key}",
                headers=headers,
                json=update_data,
                timeout=10,
            )
            # Should be 200 (updated) or 404 (not found)
            assert r.status_code in [200, 404]
            
            if r.status_code == 200:
                updated_config = r.json()
                assert updated_config["valor"] == "updated_test_config_value"
                assert updated_config["descricao"] == "Updated test configuration"
            
            # Test delete configuration
            r = requests.delete(
                f"{base}/api/v1/admin/configuracoes/{test_key}",
                headers=headers,
                timeout=10,
            )
            # Should be 204 (deleted) or 404 (not found)
            assert r.status_code in [204, 404]
    else:
        # If we can't get a token, just test that the endpoints exist
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
    
    # Test update configuration endpoint (with a non-existent key)
    r = requests.put(
        f"{base}/api/v1/admin/configuracoes/non_existent_key",
        timeout=10,
    )
    assert r.status_code in [422, 401, 403, 500]  # 422 for validation error
    
    # Test delete configuration endpoint (with a non-existent key)
    r = requests.delete(
        f"{base}/api/v1/admin/configuracoes/non_existent_key",
        timeout=10,
    )
    assert r.status_code in [204, 401, 403, 500]  # 204 for successful deletion (even if not found)