import requests
import json
import os

def test_api_key_authentication():
    """
    Test script to verify API key authentication is working
    """
    # Configuration
    api_base_url = os.getenv("SENSORIUM_API_BASE_URL", "http://localhost:8000")
    api_key = os.getenv("SENSORIUM_API_KEY", "")  # API key from sensor registration
    user_token = os.getenv("SENSORIUM_TOKEN", "")  # User token for fallback
    dispositivo_id = int(os.getenv("SENSORIUM_DISPOSITIVO_ID", "1"))
    
    print("Testing API Key Authentication Implementation")
    print("="*50)
    print(f"API Base URL: {api_base_url}")
    print(f"API Key: {'Provided' if api_key else 'NOT PROVIDED'}")
    print(f"User Token: {'Provided' if user_token else 'NOT PROVIDED'}")
    print(f"Dispositivo ID: {dispositivo_id}")
    print()
    
    # Test 1: Send data with API key in header
    if api_key:
        print("Test 1: Sending data with API key authentication")
        headers_with_api_key = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        data = {
            "ph": 7.2,
            "boia": 1,
            "status_boia": "ALTO",
            "dispositivo_id": dispositivo_id  # This will be overridden by API key auth
        }
        
        try:
            response = requests.post(
                f"{api_base_url}/api/v1/leituras/",
                headers=headers_with_api_key,
                json=data,
                timeout=10
            )
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            if response.status_code in [200, 201]:
                print("✓ API key authentication SUCCESSFUL")
            else:
                print(f"✗ API key authentication FAILED with status {response.status_code}")
        except Exception as e:
            print(f"✗ API key authentication ERROR: {e}")
        
        print()
    
    # Test 2: Send data with user token (for backward compatibility)
    if user_token:
        print("Test 2: Sending data with user token authentication (backward compatibility)")
        headers_with_token = {
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "ph": 7.3,
            "boia": 0,
            "status_boia": "BAIXO",
            "dispositivo_id": dispositivo_id
        }
        
        try:
            response = requests.post(
                f"{api_base_url}/api/v1/leituras/",
                headers=headers_with_token,
                json=data,
                timeout=10
            )
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            if response.status_code in [200, 201]:
                print("✓ User token authentication SUCCESSFUL")
            else:
                print(f"✗ User token authentication FAILED with status {response.status_code}")
        except Exception as e:
            print(f"✗ User token authentication ERROR: {e}")
        
        print()
    
    # Test 3: Send data with both headers (testing priority)
    if api_key and user_token:
        print("Test 3: Sending data with both API key and user token")
        headers_with_both = {
            'X-API-Key': api_key,
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "ph": 7.4,
            "boia": 1,
            "status_boia": "ALTO",
            "dispositivo_id": 999  # This should be overridden by API key
        }
        
        try:
            response = requests.post(
                f"{api_base_url}/api/v1/leituras/",
                headers=headers_with_both,
                json=data,
                timeout=10
            )
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            if response.status_code in [200, 201]:
                print("✓ Both headers authentication SUCCESSFUL")
            else:
                print(f"✗ Both headers authentication FAILED with status {response.status_code}")
        except Exception as e:
            print(f"✗ Both headers authentication ERROR: {e}")
        
        print()
    
    # Test 4: Send data without any authentication (should fail)
    print("Test 4: Sending data without any authentication (should fail)")
    headers_without_auth = {
        'Content-Type': 'application/json'
    }
    data = {
        "ph": 7.5,
        "boia": 1,
        "status_boia": "ALTO",
        "dispositivo_id": dispositivo_id
    }
    
    try:
        response = requests.post(
            f"{api_base_url}/api/v1/leituras/",
            headers=headers_without_auth,
            json=data,
            timeout=10
        )
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        if response.status_code == 401:
            print("✓ No authentication correctly REJECTED (401 Unauthorized)")
        else:
            print(f"✗ No authentication should have been REJECTED, got {response.status_code}")
    except Exception as e:
        print(f"✗ No authentication test ERROR: {e}")

def test_sensor_registration():
    """
    Test if sensor registration still works and returns API key
    """
    api_base_url = os.getenv("SENSORIUM_API_BASE_URL", "http://localhost:8000")
    user_token = os.getenv("SENSORIUM_TOKEN", "")
    
    if not user_token:
        print("Cannot test sensor registration - no user token provided")
        return
    
    print("Testing Sensor Registration")
    print("="*30)
    
    headers = {
        'Authorization': f'Bearer {user_token}',
        'Content-Type': 'application/json'
    }
    
    sensor_data = {
        "nome": "Test Sensor API Key",
        "tipo": "TESTE",
        "descricao": "Sensor de teste para autenticação por chave de API"
    }
    
    try:
        response = requests.post(
            f"{api_base_url}/api/v1/sensores/registrar-sensor",
            headers=headers,
            json=sensor_data,
            timeout=10
        )
        
        print(f"Registration Response Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"Sensor ID: {result.get('id')}")
            print(f"Sensor Name: {result.get('nome')}")
            print(f"API Key: {result.get('chave_api')[:10]}..." if result.get('chave_api') else "No API key returned")
            print("✓ Sensor registration SUCCESSFUL")
            return result.get('chave_api'), result.get('id')
        else:
            print(f"✗ Sensor registration FAILED: {response.text}")
            return None, None
    except Exception as e:
        print(f"✗ Sensor registration ERROR: {e}")
        return None, None

if __name__ == "__main__":
    print("Running API Key Authentication Tests")
    print("="*60)
    
    # First, test sensor registration if needed
    api_key, sensor_id = test_sensor_registration()
    
    if api_key:
        print(f"\nUsing newly registered API key for tests: {api_key[:10]}...")
        os.environ['SENSORIUM_API_KEY'] = api_key
    
    print()
    test_api_key_authentication()