#!/usr/bin/env python3
"""
Deployment Health Check Script
Verifies all components are configured correctly before deploying to Render.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("DEPLOYMENT HEALTH CHECK")
print("=" * 60)

errors = []
warnings = []

# Check 1: Environment Variables
print("\n[1] Checking Environment Variables...")
required_vars = {
    "QDRANT_URL": os.getenv("QDRANT_URL"),
    "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY"),
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
}

for var_name, var_value in required_vars.items():
    if var_value:
        print(f"  ✅ {var_name}: Set")
    else:
        print(f"  ❌ {var_name}: MISSING")
        errors.append(f"Missing environment variable: {var_name}")

# Check 2: Python Version
print("\n[2] Checking Python Version...")
python_version = sys.version_info
print(f"  Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major == 3 and python_version.minor >= 11:
    print("  ✅ Python version OK")
else:
    warnings.append(f"Python {python_version.major}.{python_version.minor} - Recommended: 3.11+")

# Check 3: Required Files
print("\n[3] Checking Required Files...")
required_files = [
    "server.py",
    "rag_system.py",
    "requirements.txt",
    "Procfile",
]

for file in required_files:
    if os.path.exists(file):
        print(f"  ✅ {file}: Exists")
    else:
        print(f"  ❌ {file}: MISSING")
        errors.append(f"Missing file: {file}")

# Check 4: Import Test
print("\n[4] Testing Imports...")
try:
    import fastapi
    print("  ✅ fastapi: OK")
except ImportError:
    print("  ❌ fastapi: FAILED")
    errors.append("fastapi not installed")

try:
    import uvicorn
    print("  ✅ uvicorn: OK")
except ImportError:
    print("  ❌ uvicorn: FAILED")
    errors.append("uvicorn not installed")

try:
    from qdrant_client import QdrantClient
    print("  ✅ qdrant-client: OK")
except ImportError:
    print("  ❌ qdrant-client: FAILED")
    errors.append("qdrant-client not installed")

try:
    from groq import Groq
    print("  ✅ groq: OK")
except ImportError:
    print("  ❌ groq: FAILED")
    errors.append("groq not installed")

try:
    from sentence_transformers import SentenceTransformer
    print("  ✅ sentence-transformers: OK")
except ImportError:
    print("  ❌ sentence-transformers: FAILED")
    errors.append("sentence-transformers not installed")

# Check 5: Server Import Test
print("\n[5] Testing Server Import...")
try:
    from server import app
    print("  ✅ server.py: Imports successfully")
except Exception as e:
    print(f"  ❌ server.py: Import failed - {str(e)}")
    errors.append(f"server.py import error: {str(e)}")

# Check 6: Health Endpoint Test
print("\n[6] Testing Health Endpoint...")
try:
    from server import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    
    if response.status_code == 200:
        print(f"  ✅ /health: Returns {response.status_code}")
        print(f"     Response: {response.json()}")
    else:
        print(f"  ⚠️  /health: Returns {response.status_code}")
        warnings.append(f"Health endpoint returned {response.status_code}")
except Exception as e:
    print(f"  ⚠️  /health: Test failed - {str(e)}")
    warnings.append(f"Health endpoint test error: {str(e)}")

# Check 7: RAG System Test (Optional - may be slow)
print("\n[7] Testing RAG System (Optional)...")
test_rag = os.getenv("TEST_RAG", "false").lower() == "true"
if test_rag:
    try:
        from rag_system import RAGSystem
        print("  ⏳ Initializing RAG system (this may take 30-60 seconds)...")
        rag = RAGSystem()
        print("  ✅ RAG system: Initialized successfully")
    except Exception as e:
        print(f"  ❌ RAG system: Initialization failed - {str(e)}")
        errors.append(f"RAG system error: {str(e)}")
else:
    print("  ⏭️  Skipping (set TEST_RAG=true to test)")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if errors:
    print(f"\n❌ ERRORS FOUND: {len(errors)}")
    for error in errors:
        print(f"  • {error}")
    print("\n⚠️  Fix errors before deploying!")
    sys.exit(1)
else:
    print("\n✅ No critical errors found")

if warnings:
    print(f"\n⚠️  WARNINGS: {len(warnings)}")
    for warning in warnings:
        print(f"  • {warning}")

print("\n" + "=" * 60)
print("Next Steps:")
print("1. Fix any errors above")
print("2. Deploy to Render")
print("3. Check Render logs after deployment")
print("4. Test: curl https://fragmentstothought.onrender.com/health")
print("=" * 60)
