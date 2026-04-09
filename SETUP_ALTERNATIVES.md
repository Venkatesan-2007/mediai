# Medical AI - Setup Alternatives for Installation Issues

If you're experiencing errors when installing dependencies, here are alternative solutions:

---

## Option 1: Docker Compose (Recommended ✅)
**Best for:** Windows, Mac, Linux - if Docker is installed

This requires NO local Python installation!

```bash
# Navigate to project directory
cd medi ai

# Start all services (backend, frontend, database)
docker-compose up --build

# Services will be available at:
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Database: localhost:5432
```

**To stop:**
```bash
docker-compose down
```

---

## Option 2: Minimal Requirements Installation
**Best for:** If you want to run locally but have pip errors

Use the minimal requirements file with only essential packages:

```bash
# Activate virtual environment
.venv\Scripts\activate.bat

# Install minimal dependencies (faster, fewer issues)
pip install -r backend/requirements-minimal.txt

# For OCR/ML features later, install individually:
pip install paddleocr paddlepaddle scikit-learn
```

---

## Option 3: Clean Virtual Environment (Fresh Start)
**Best for:** Corrupted environment or conflicting packages

```bash
# Backup old environment (optional)
rmdir /s .venv

# Create fresh virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate.bat

# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r backend/requirements.txt
```

---

## Option 4: Step-by-Step Manual Installation
**Best for:** Debugging specific package issues

```bash
# Activate venv
.venv\Scripts\activate.bat

# Install in groups with error handling
echo "Installing web framework..."
pip install fastapi==0.104.1 uvicorn==0.24.0 python-multipart==0.0.6

echo "Installing data processing..."
pip install numpy pandas scipy

echo "Installing vector database..."
pip install chromadb sentence-transformers

echo "Installing database..."
pip install sqlalchemy psycopg2-binary

echo "Installing authentication..."
pip install bcrypt python-jose

echo "Installing utilities..."
pip install python-dotenv pydantic requests httpx slowapi

echo "Done!"
```

---

## Option 5: Conda Environment (Alternative)
**Best for:** Mac/Linux users with conda installed

```bash
# Create conda environment
conda create -n mediai python=3.11

# Activate
conda activate mediai

# Install from requirements
pip install -r backend/requirements-minimal.txt
```

---

## Common Issues & Solutions

### Issue: "No matching distribution found for numpy"
**Solution:** Use Option 3 (Clean Virtual Environment) - your pip cache is corrupted

### Issue: "Microsoft Visual Studio is not installed"
**Solution:** Use Docker Compose (Option 1) - no C++ compiler needed

### Issue: "Permission denied" or "site-packages is not writeable"
**Solution:** Use fresh venv (Option 3) or Docker (Option 1)

### Issue: Multiple dependency conflicts
**Solution:** Use minimal requirements (Option 2) first, add packages as needed

---

## Testing Installation

After installing, test if it works:

```bash
# Test Python packages
python -c "import fastapi; print('FastAPI OK')"
python -c "import chromadb; print('ChromaDB OK')"
python -c "import pandas; print('Pandas OK')"

# Run backend
cd backend
uvicorn main:app --reload
```

---

## Recommended: Use Docker Compose

If you have Docker installed, this is the simplest:

```bash
docker-compose up --build
```

No pip, no conflicts, no version issues - everything works!

---

## Need Help?

If you're still having issues with a specific package, let me know:
- The exact error message
- Your operating system
- What you already tried

I can create a custom solution for your specific case.
