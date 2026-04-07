"""
Test script to check chat API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# First, register a test user
print("1. Registering test user...")
try:
    resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={"username": "testchat2", "password": "testpass123"},
        timeout=5
    )
    if resp.status_code == 200:
        user_data = resp.json()
        token = user_data['access_token']
        print(f"✓ Registered and got token: {token[:20]}...")
    else:
        print(f"✗ Register failed: {resp.status_code} - {resp.text[:100]}")
        # Try login instead
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "testchat2", "password": "testpass123"},
            timeout=5
        )
        if resp.status_code == 200:
            user_data = resp.json()
            token = user_data['access_token']
            print(f"✓ Logged in: {token[:20]}...")
        else:
            print(f"✗ Login also failed: {resp.text[:100]}")
            exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Check status
print("\n2. Checking API status...")
try:
    resp = requests.get(f"{BASE_URL}/api/status", timeout=5)
    print(f"Status: {resp.json()}")
except Exception as e:
    print(f"✗ Error: {e}")

# Check LLM diagnostics
print("\n3. Checking LLM diagnostics...")
try:
    resp = requests.get(f"{BASE_URL}/api/llm-diagnostics", timeout=5)
    llm_data = resp.json()
    print(f"LLM Type: {llm_data['llm_type']}")
    print(f"Available: {llm_data['is_available']}")
    print(f"Status: {llm_data['status']}")
    if llm_data.get('error_details'):
        print(f"Error: {llm_data['error_details']}")
except Exception as e:
    print(f"✗ Error: {e}")

# Now test the chat endpoint
print("\n4. Testing chat endpoint...")
try:
    resp = requests.post(
        f"{BASE_URL}/api/chat",
        json={"question": "What are the core elements?", "mode": "rag"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Answer: {data.get('answer', 'N/A')[:200]}...")
    print(f"Sources: {data.get('sources', [])}")
except Exception as e:
    print(f"✗ Error: {e}")

