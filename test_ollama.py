#!/usr/bin/env python
"""Test Ollama service"""
import requests

base_url = 'http://localhost:11434'

# Test Ollama connection
print('Testing Ollama connection...')
try:
    resp = requests.get(f'{base_url}/api/tags', timeout=3)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        models = data.get('models', [])
        print(f'Available models: {len(models)}')
        for model in models:
            print(f'  - {model.get("name", "unknown")}')
    else:
        print(f'Error: {resp.text}')
except requests.exceptions.ConnectionError as e:
    print(f'✗ Connection Error - Ollama is not running at {base_url}')
except Exception as e:
    print(f'Error: {e}')

# Test generation
print('\nTesting text generation...')
try:
    resp = requests.post(
        f'{base_url}/api/generate',
        json={
            'model': 'mistral',
            'prompt': 'What is 2+2?',
            'stream': False,
        },
        timeout=60
    )
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'Response: {data.get("response", "N/A")[:100]}')
    else:
        print(f'Error: {resp.status_code}')
        print(f'Response: {resp.text[:300]}')
except requests.exceptions.Timeout:
    print('✗ Request timed out - Ollama might be slow or unresponsive')
except Exception as e:
    print(f'Error: {e}')
