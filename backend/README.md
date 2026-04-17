# Medi AI Backend

Welcome to the Medi AI backend documentation! This guide will help you understand, develop, and extend the backend system.

## 🎯 Quick Start

**New to the codebase?** Start here:

1. **5 minutes**: Read [Backend Architecture Overview](STRUCTURE.md)
2. **10 minutes**: Skim [Features Directory README](features/README.md)
3. **15 minutes**: Pick a feature, read its README:
   - [Auth Feature](features/auth/README.md) - User authentication
   - [Books Feature](features/books/README.md) - PDF processing
   - [Chat Feature](features/chat/README.md) - AI chat interface
   - [Dashboard Feature](features/dashboard/README.md) - Analytics
   - [Shared Feature](features/shared/README.md) - Core infrastructure
4. **20 minutes**: Run the application (see below)

**Total**: 1 hour to understand the entire backend system

---

## 📁 Project Structure

```
backend/
├── features/                    # ⭐ MAIN APPLICATION CODE
│   ├── auth/                    # User authentication & JWT tokens
│   ├── books/                   # PDF upload, processing, search
│   ├── chat/                    # AI chat with LLM integration
│   ├── dashboard/               # User analytics & progress
│   ├── shared/                  # Core infrastructure (database, vectors, cache)
│   └── README.md                # Feature architecture guide
│
├── database/                    # SQLite database files
│   └── chroma_db/               # Vector embeddings storage
│
├── prompts/                     # LLM system prompts
│   └── medical_prompt.txt
│
├── main.py                      # ⭐ FastAPI application entry point
├── requirements.txt             # Python dependencies
├── STRUCTURE.md                 # Complete architecture reference
├── Dockerfile                   # Container configuration
├── docker-compose.yml           # Container orchestration
└── README.md                    # ⭐ You are here
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip or conda
- Git

### Installation

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Windows)
venv\Scripts\activate
# Or (Mac/Linux)
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file with API keys
# Copy from .env.example or create new:
echo "SECRET_KEY=your-secret-key-here
SAMBANOVA_API_KEY=your-api-key-here
DATABASE_URL=sqlite:///./database/medi_ai.db" > .env
```

### Run Development Server

```bash
# Start FastAPI development server
python main.py

# Or with auto-reload
python -m uvicorn main:app --reload

# Server runs at: http://localhost:8000
# API docs: http://localhost:8000/docs
# Alternative docs: http://localhost:8000/redoc
```

### Test the API

```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123"}'

# Get current user (replace TOKEN)
TOKEN="eyJ0eXAi..."
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🏗️ Architecture Overview

### Technology Stack

```
┌─────────────────────────────────────────────┐
│         Client (React Frontend)             │
│  Sends HTTP requests, displays responses    │
└────────────────────┬────────────────────────┘
                     │ HTTP/JSON
                     │
┌────────────────────▼────────────────────────┐
│     FastAPI Framework (main.py)             │
│  Routes → Validate → Services → Database    │
└────────────────────┬────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐  ┌──────▼──────┐  ┌────▼────┐
│   Auth  │  │    Books    │  │  Chat   │  Features
│Service  │  │  Services   │  │Services │
└────┬────┘  └──────┬──────┘  └────┬────┘
     │               │              │
     └───────────────┼──────────────┘
                     │
         ┌───────────▼──────────┐
         │ Shared Core Features │
         │ Database + Vectors   │
         │ SQLAlchemy + FAISS   │
         └───────────┬──────────┘
                     │
         ┌───────────▼──────────┐
         │  SQLite Database +   │
         │  FAISS Vector Index  │
         └──────────────────────┘

External Services:
- SambaNova API: Generate embeddings & chat
- Ollama: Local LLM (if running)
- Tesseract OCR: Text extraction from images
```

### Design Patterns Used

**1. Feature-Based Architecture**
```
Why?
- Group related code together
- Easy to share features with team
- Clear dependencies between features
- Matches frontend structure

Example:
auth/
├── services/     (auth logic)
├── models/       (schemas)
├── routes/       (API endpoints)
└── README.md     (documentation)
```

**2. Service Layer Pattern**
```
API Route → Service → Database
   ↓          ↓          ↓
validate   business   persistence
           logic
```

**3. Dependency Injection**
```
# FastAPI auto-injects dependencies
@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    # db is automatically created and closed
    return db.query(User).all()
```

---

## 📚 Key Concepts

### Authentication & Security

**Password Hashing (Bcrypt)**
- One-way encryption
- Intentionally slow (prevents brute force)
- Salt prevents rainbow table attacks
- Read: [Auth Feature Guide](features/auth/README.md)

**JWT Tokens**
- Stateless authentication
- Client carries token in request headers
- 24-hour expiration
- Signed with SECRET_KEY

### Document Processing

**PDF Extraction**
- Uses pdfplumber to convert binary PDFs to text
- Handles multiple pages and formats
- Read: [Books Feature - PDF Loading](features/books/README.md#core-concepts)

**Text Chunking**
- Splits documents into 500-character overlapping chunks
- Preserves context across boundaries
- Read: [Books Feature - Text Chunking](features/books/README.md#core-concepts)

**Semantic Search (FAISS)**
- Converts text to 1536-dimensional vectors
- Fast similarity search (O(log n) time)
- Finds contextually relevant documents
- Read: [Books Feature - FAISS](features/books/README.md#core-concepts)

### AI Integration

**Retrieval-Augmented Generation (RAG)**
- Searches user documents for context
- Augments LLM prompt with retrieved chunks
- Provides accurate, sourced responses
- Read: [Chat Feature Guide](features/chat/README.md#core-concepts)

---

## 🔑 Environment Variables

```bash
# Required
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///./database/medi_ai.db
# or: postgresql://user:pass@localhost/medi_ai

# API Keys
SAMBANOVA_API_KEY=your-sambanova-key
SAMBANOVA_BASE_URL=https://api.sambanova.ai/v1

# Optional: Local LLM
OLLAMA_BASE_URL=http://localhost:11434
LOCAL_MODEL_NAME=llama2

# Embeddings
EMBEDDING_DIMENSION=1536
EMBEDDING_MODEL=text-embedding-3-small

# Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Token expiration
ACCESS_TOKEN_EXPIRE_HOURS=24
ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
```

Create `.env` file in backend directory with these variables.

---

## 🧪 Testing

### Run Tests

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=features tests/
```

### Test Manually with curl

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"Pass123!"}'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"Pass123!"}' | jq -r '.access_token')

# Get current user
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Upload PDF
curl -X POST http://localhost:8000/api/books/upload \
  -F "file=@document.pdf" \
  -H "Authorization: Bearer $TOKEN"

# Search documents
curl -X POST http://localhost:8000/api/books/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"cardiac disease"}'

# Chat
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is heart disease?"}'

# Get dashboard
curl http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📖 API Documentation

### Auto-Generated Docs

When server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These show all endpoints with:
- Parameter descriptions
- Request/response examples
- Try-it-out interface

### Endpoint Categories

**Authentication** - `/api/auth/`
- `POST /register` - Create new user
- `POST /login` - User login
- `GET /me` - Get current user
- `POST /logout` - User logout

**Books** - `/api/books/`
- `POST /upload` - Upload PDF
- `GET /` - List user's books
- `POST /search` - Search documents
- `DELETE /{id}` - Delete book

**Chat** - `/api/chat/`
- `POST /message` - Send chat message
- `GET /history` - Get conversation history
- `DELETE /history` - Clear history

**Dashboard** - `/api/dashboard/`
- `GET /stats` - User statistics
- `GET /progress` - Learning progress
- `GET /activity` - Activity chart

---

## 🐛 Debugging

### View Logs

```bash
# Tail application logs (if configured)
tail -f backend/logs/app.log

# Or check console output when running main.py
```

### Debug with Breakpoints

```python
# Add breakpoint in code
def some_function():
    import pdb; pdb.set_trace()  # Pauses execution here
    code_here()
```

### Common Issues

**"Module not found" error**
```bash
# Make sure you're in backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

**"SAMBANOVA_API_KEY not found"**
```bash
# Check .env file exists
ls -la .env

# Check key is set
source .env
echo $SAMBANOVA_API_KEY

# Or see how it's loaded in main.py
```

**Database locked**
```bash
# SQLite issue: close all connections
# Stop all running servers
# Delete database/medi_ai.db (will recreate)
rm database/medi_ai.db

# Restart server
python main.py
```

---

## 📦 Dependencies

Main dependencies:

```
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
sqlalchemy==2.0.0         # Database ORM
pydantic==2.0.0           # Data validation
python-jose==3.3.0        # JWT tokens
passlib==1.7.4            # Password hashing
bcrypt==4.1.0             # Bcrypt hashing
pdfplumber==0.10.0        # PDF text extraction
python-multipart==0.0.6   # File uploads
requests==2.31.0          # HTTP client
faiss-cpu==1.7.4          # Vector search (or faiss-gpu)
python-dotenv==1.0.0      # Environment variables
```

See [requirements.txt](requirements.txt) for full list and versions.

---

## 🔒 Security Best Practices

**Implemented:**
- ✅ Password hashing with bcrypt
- ✅ JWT tokens with expiration
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ User isolation (filtering by user_id)
- ✅ Environment variables for secrets
- ✅ HTTPS (in production)

**To Do:**
- [ ] Rate limiting on auth endpoints
- [ ] CORS configuration for frontend
- [ ] Request validation on all endpoints
- [ ] Logging of security events
- [ ] API key rotation strategy
- [ ] Database backup strategy

---

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t medi-ai-backend .

# Run container
docker run -p 8000:8000 \
  -e SAMBANOVA_API_KEY=your-key \
  -e DATABASE_URL=postgresql://... \
  medi-ai-backend

# Or use docker-compose
docker-compose up -d
```

### Environment Variables (Production)

Before deploying, set in production server:

```bash
# Update these
export SECRET_KEY=production-secret-key-here
export SAMBANOVA_API_KEY=production-api-key
export DATABASE_URL=postgresql://user:pass@host/dbname
export LOG_LEVEL=INFO

# Optional
export ACCESS_TOKEN_EXPIRE_HOURS=24
export CORS_ORIGINS=https://yourdomain.com
```

### Monitoring

```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG

# Monitor API usage
# Set up monitoring with Sentry/DataDog

# Set up alerts for:
# - API response time > 1s
# - Error rate > 1%
# - Database connection issues
# - API quota usage
```

---

## 🤝 Contributing

### Adding a New Feature

1. **Create feature folder**
   ```bash
   mkdir features/new_feature/{services,models,routes}
   ```

2. **Create services**
   ```bash
   touch features/new_feature/services/new_service.py
   ```

3. **Add comprehensive documentation**
   - Docstrings with WHY, WHAT, HOW
   - Inline comments explaining logic
   - Examples in docstrings

4. **Create API routes**
   ```bash
   touch features/new_feature/routes/routes.py
   ```

5. **Write tests**
   ```bash
   touch tests/test_new_feature.py
   ```

6. **Register routes in main.py**
   ```python
   from features.new_feature.routes import routes
   app.include_router(routes.router, prefix="/api/new_feature")
   ```

### Code Style

```python
# Follow PEP 8
# Use type hints
def process_data(data: str) -> dict:
    """Use comprehensive docstrings"""
    # Explain WHY not just WHAT
    result = {}
    return result

# Avoid
def f(x):
    # process
    return x
```

---

## 🔗 Related Projects

**Frontend:** [../frontend/medi-ai/](../frontend/medi-ai/)
- React application
- Connects to this backend via HTTP

**Database:** [./database/](./database/)
- SQLite for development
- PostgreSQL for production

---

## 📚 Further Reading

- [Complete Architecture Reference](STRUCTURE.md) - Detailed system design
- [Features README](features/README.md) - Feature organization
- [Auth Feature](features/auth/README.md) - Authentication deep dive
- [Books Feature](features/books/README.md) - PDF processing deep dive
- [Chat Feature](features/chat/README.md) - LLM integration
- [Dashboard Feature](features/dashboard/README.md) - Analytics
- [Shared Feature](features/shared/README.md) - Core infrastructure

---

## ❓ FAQ

**Q: How do I add a new API endpoint?**
A: Create a function in `features/feature/routes/`, use FastAPI decorators (`@app.post`, etc.), and add comprehensive docstrings.

**Q: How do I add a new database model?**
A: Create a class in `features/shared/models/` that inherits from `Base`, define columns and relationships, then import in `database_service.py`.

**Q: How do embeddings work?**
A: They convert text to 1536-dimensional vectors. Semantically similar texts have similar vectors. FAISS uses this for fast search.

**Q: Can I run without the SambaNova API?**
A: Yes! Use the `local_llm` service with Ollama to run models locally. No API key needed, but requires GPU.

**Q: How do I debug authentication issues?**
A: Check the token in Authorization header, verify signature with `verify_access_token()`, and check expiration time.

**Q: Where do I configure search quality?**
A: Chunk parameters (size, overlap) and `SEARCH_TOP_K` (how many results) in environment variables.

---

## 📞 Support

Having issues?

1. **Check documentation:**
   - This README
   - Feature-specific READMEs in `features/`
   - STRUCTURE.md for architecture

2. **Search logs:**
   - Terminal output
   - `backend/logs/app.log`
   - API error responses

3. **Debug:**
   - Enable DEBUG logging
   - Add breakpoints with pdb
   - Test endpoints with curl

---

## 📝 License

Medi AI Backend © 2024

---

## Version History

**v1.0 (April 2026)**
- ✅ Feature-based architecture
- ✅ Auth service with JWT tokens
- ✅ PDF processing pipeline
- ✅ Semantic search with FAISS
- ✅ LLM chat integration
- ✅ User analytics dashboard
- ✅ Comprehensive documentation

---

**Happy coding! 🚀**

For architecture questions, start with [STRUCTURE.md](STRUCTURE.md)  
For feature questions, start with [features/README.md](features/README.md)  
For specific features, read [features/{feature}/README.md](features/)
