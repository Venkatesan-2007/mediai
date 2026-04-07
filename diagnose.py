#!/usr/bin/env python
"""
Diagnostic script to test backend setup
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

print("=" * 60)
print("BACKEND DIAGNOSTIC CHECK")
print("=" * 60)

# Check Python version
print(f"\n✓ Python: {sys.version}")

# Check imports
print("\n📦 Checking imports...")
try:
    import fastapi
    print(f"  ✓ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"  ✗ FastAPI: {e}")

try:
    import uvicorn
    print(f"  ✓ Uvicorn")
except ImportError as e:
    print(f"  ✗ Uvicorn: {e}")

try:
    import faiss
    print(f"  ✓ FAISS")
except ImportError as e:
    print(f"  ✗ FAISS: {e}")

try:
    from dotenv import load_dotenv
    print(f"  ✓ python-dotenv")
except ImportError as e:
    print(f"  ✗ python-dotenv: {e}")

try:
    from sqlalchemy import create_engine
    print(f"  ✓ SQLAlchemy")
except ImportError as e:
    print(f"  ✗ SQLAlchemy: {e}")

# Check environment variables
print("\n🔑 Environment variables:")
load_dotenv(Path(__file__).parent / '.env')
print(f"  OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'NOT SET')}")
print(f"  OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'NOT SET')}")

# Test Ollama connection
print("\n🔗 Testing Ollama connection...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print(f"  ✓ Ollama is running - {len(models)} models available")
        for model in models[:3]:
            print(f"    - {model.get('name', 'Unknown')}")
    else:
        print(f"  ✗ Ollama responded with status {response.status_code}")
except Exception as e:
    print(f"  ✗ Cannot connect to Ollama: {e}")

# Check database
print("\n💾 Database setup:")
try:
    db_path = Path(__file__).parent / 'backend' / 'database'
    print(f"  Database path: {db_path}")
    print(f"  Exists: {db_path.exists()}")
    if db_path.exists():
        print(f"  Contents: {list(db_path.glob('*'))[:5]}")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC CHECK COMPLETE")
print("=" * 60)
