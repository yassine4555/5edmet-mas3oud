"""
API Verification Script for SAVING_SERVER
Tests all endpoints to ensure they work correctly.
"""

import requests
import json
import os

BASE_URL = "http://localhost:5001"
API_KEY = "nexus-internal-secret-key-123"
HEADERS = {
    "X-Internal-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_health():
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_create_user():
    print("\n=== Testing Create User ===")
    user_data = {
        "email": "test@example.com",
        "userID": "auth0_test_123",
        "password": "placeholder",
        "role": "employee",
        "first_name": "Test",
        "last_name": "User",
        "address": "123 Test St",
        "department": "QA",
        "date_of_birth": "1990-01-01"
    }
    response = requests.post(f"{BASE_URL}/users/", headers=HEADERS, json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code in [200, 201, 409]  # 409 if already exists

def test_get_users():
    print("\n=== Testing Get Users ===")
    response = requests.get(f"{BASE_URL}/users/", headers=HEADERS)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data.get('data', []))} users")
    assert response.status_code == 200

def test_create_invite():
    print("\n=== Testing Create Invite ===")
    invite_data = {
        "manager_id": "auth0_manager_456",
        "code": "TEST1234",
        "max_uses": 5
    }
    response = requests.post(f"{BASE_URL}/invites/", headers=HEADERS, json=invite_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code in [200, 201, 409]  # 409 if already exists

def test_file_upload():
    print("\n=== Testing File Upload ===")
    # Create a test file
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for SAVING_SERVER")
    
    try:
        files = {'file': open(test_file_path, 'rb')}
        data = {'user_email': 'admin@example.com'}
        headers_no_content_type = {"X-Internal-Key": API_KEY}
        
        response = requests.post(f"{BASE_URL}/file/upload", 
                                headers=headers_no_content_type, 
                                files=files, 
                                data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_get_all_files():
    print("\n=== Testing Get All Files ===")
    response = requests.get(f"{BASE_URL}/file/getAll", headers=HEADERS)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data.get('files', []))} files")
    assert response.status_code == 200

def test_unauthorized():
    print("\n=== Testing Unauthorized Access ===")
    response = requests.get(f"{BASE_URL}/users/")  # No API key
    print(f"Status: {response.status_code}")
    assert response.status_code == 401

if __name__ == "__main__":
    print("Starting SAVING_SERVER API Tests...")
    print("Make sure the server is running: python app.py")
    print("And the database is seeded: python seed.py")
    
    try:
        test_health()
        test_unauthorized()
        test_create_user()
        test_get_users()
        test_create_invite()
        test_file_upload()
        test_get_all_files()
        
        print("\n" + "="*50)
        print("✅ All tests passed!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server. Make sure it's running on port 5001")
    except Exception as e:
        print(f"\n❌ Error: {e}")
