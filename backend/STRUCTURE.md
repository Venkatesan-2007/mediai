# Backend Architecture Guide

## Project Structure

```
backend/
├── features/                          # ⭐ Feature modules (main application code)
│   ├── auth/                          # User authentication & security
│   │   ├── services/
│   │   │   ├── auth_service.py        # Password hashing, JWT tokens (500+ lines)
│   │   │   └── __init__.py
│   │   ├── models/                    # Pydantic request/response models
│   │   ├── routes/                    # FastAPI endpoints (/api/auth/*)
│   │   └── README.md                  # Feature documentation
│   │
│   ├── books/                         # PDF upload, processing, storage
│   │   ├── services/
│   │   │   ├── pdf_loader_service.py  # Extract text from PDFs (300+ lines)
│   │   │   ├── embeddings_service.py  # Convert text to vectors (350+ lines)
│   │   │   ├── chunking_service.py    # Split text into chunks (PENDING)
│   │   │   ├── ocr_service.py         # Extract text from images (PENDING)
│   │   │   └── __init__.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── README.md
│   │
│   ├── chat/                          # AI chat & LLM services
│   │   ├── services/
│   │   │   ├── local_llm.py           # Local Ollama model service (PENDING)
│   │   │   ├── sambanova_api.py       # SambaNova API integration (PENDING)
│   │   │   ├── ollama_service.py      # Ollama-specific methods (PENDING)
│   │   │   ├── normal_model_service.py # Standard LLM service (PENDING)
│   │   │   ├── cache.py               # Chat cache service (PENDING)
│   │   │   └── __init__.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── README.md
│   │
│   ├── dashboard/                     # User statistics & analytics
│   │   ├── services/
│   │   │   └── analytics_service.py   # User stats & metrics (PENDING)
│   │   ├── models/
│   │   ├── routes/
│   │   └── README.md
│   │
│   ├── shared/                        # Shared services for all features
│   │   ├── services/
│   │   │   ├── database_service.py    # SQLAlchemy ORM models (400+ lines)
│   │   │   ├── vector_store_service.py # FAISS semantic search (400+ lines)
│   │   │   ├── cache.py               # Caching utilities (PENDING)
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── user.py                # User model
│   │   │   ├── book.py                # Book/PDF model
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   │   ├── validators.py          # Input validation (PENDING)
│   │   │   ├── errors.py              # Custom exceptions (PENDING)
│   │   │   └── helpers.py             # Utility functions (PENDING)
│   │   └── README.md
│   │
│   └── README.md                      # ⭐ Start here for backend overview
│
├── database/                          # 📁 SQLite database files
│   └── chroma_db/                     # ChromaDB vector database
│       ├── chroma.sqlite3
│       └── [index files]
│
├── prompts/                           # 📝 LLM system prompts
│   └── medical_prompt.txt             # Instructions for medical AI
│
├── main.py                            # ⭐ FastAPI application entry point
├── requirements.txt                   # Python package dependencies
├── Dockerfile                         # Docker container configuration
└── STRUCTURE.md                       # ⭐ You are here (architecture overview)
```

---

## Why Feature-Based Architecture?

### ❌ Problems with Service-Based (Flat)
```
backend/services/
├── auth.py         (Password hashing, JWT tokens)
├── pdf_loader.py   (PDF extraction)
├── embeddings.py   (Vector generation)
├── vector_store.py (Search indexing)
├── cache.py        (Caching logic)
├── chunking.py     (Text splitting)
└── ...            (10+ files all mixed together)

ISSUES:
- Hard to find related code
- Unclear which service uses which
- Can't share just "auth" with team member
- New developer loads all services at once
```

### ✅ Solutions with Feature-Based (Grouped)
```
backend/features/
├── auth/
│   ├── services/      (Only auth-related code)
│   ├── models/        (Login request/response)
│   ├── routes/        (API endpoints)
│   └── README.md      (Auth feature guide)
│
├── books/
│   ├── services/      (PDF, chunking, embeddings)
│   ├── models/
│   ├── routes/
│   └── README.md
│
└── shared/
    ├── services/      (Database, vector store)
    ├── models/        (User, Book models)
    └── README.md

BENEFITS:
✓ Group related code together
✓ Easy to share feature with others
✓ Clear dependencies between features
✓ Can develop features somewhat independently
✓ Matches frontend structure
```

---

## Service Organization

Each feature contains **specialized services**:

### 🔐 Auth Feature
**Responsibility:** Secure user authentication

| Service | Purpose | Key Function |
|---------|---------|-------------|
| `auth_service.py` | Password security & tokens | `hash_password()` creates bcrypt hash |
| | | `verify_password()` checks against hash |
| | | `create_access_token()` generates JWT |
| | | `verify_access_token()` validates JWT |

**Why Bcrypt?**
- Intentionally slow (0.3-0.5 seconds)
- Prevents brute force attacks
- Has built-in salt
- One-way encryption (can't reverse)

**Why JWT Tokens?**
- Stateless (no server database needed)
- Client carries token in headers
- Expires automatically (24 hours)
- Prevents session hijacking

---

### 📚 Books Feature
**Responsibility:** PDF management and processing

| Service | Purpose | Key Function |
|---------|---------|-------------|
| `pdf_loader_service.py` | Extract text | `load_pdf_binary()` extracts pages |
| `chunking_service.py` | Split text | `split_text()` creates overlap chunks |
| `embeddings_service.py` | Vector conversion | `embed_chunks()` API calls for vectors |
| `ocr_service.py` | Extract from images | `ocr_image()` uses Tesseract |

**Data Pipeline:**
```
User uploads PDF (binary)
    ↓
pdf_loader extracts text (concatenated pages)
    ↓
chunking_service splits on sentences (500 chars + 100 overlap)
    ↓
embeddings generates vectors (1536 dimensions)
    ↓
vector_store indexes in FAISS
    ↓
User can now search document
```

---

### 💬 Chat Feature
**Responsibility:** LLM integration and chat responses

| Service | Purpose | Key Function |
|---------|---------|-------------|
| `local_llm.py` | Local model | `generate_response()` runs Ollama locally |
| `sambanova_api.py` | Remote API | `call_api()` sends to SambaNova servers |
| `ollama_service.py` | Ollama specific | `pull_model()`, `list_models()` |
| `cache.py` | Query caching | `get_cached()` avoids re-computing |

**Why Multiple?**
- **Local:** Privacy + no cost (but slower)
- **API:** Faster + more capable (but costs $)
- **Cache:** Avoid duplicate work

---

### 📊 Dashboard Feature
**Responsibility:** User analytics and progress

| Service | Purpose | Key Function |
|---------|---------|-------------|
| `analytics_service.py` | User stats | `get_user_progress()` calculates % |
| | | `get_weak_areas()` identifies gaps |
| | | `get_study_streak()` counts days |

---

### 🔌 Shared Feature
**Responsibility:** Core infrastructure for all features

| Service | Purpose | Key Function |
|---------|---------|-------------|
| `database_service.py` | Database access | SQLAlchemy models (User, Book) |
| | | `get_user()`, `create_book()` |
| `vector_store_service.py` | Semantic search | FAISS indexing |
| | | `search()` finds similar documents |
| `cache.py` | Key-value caching | Redis or in-memory |

---

## Code Documentation Levels

### Level 1: Module Docstring (Why this file exists)
```python
"""
Auth Service
============

PURPOSE:
- Securely hash user passwords
- Generate and validate JWT tokens
- Provide authentication helpers

WHY:
- Application needs to prevent unauthorized access
- Passwords must be one-way encrypted
- Users need session tokens for stateless auth

KEY CONCEPTS:
1. Bcrypt: Intentionally slow hashing algorithm
2. JWT: JSON Web Token for stateless sessions
3. Timing-safe comparison: Prevents timing attacks
"""
```

### Level 2: Function Docstring (What, Why, How)
```python
def hash_password(password: str) -> str:
    """
    Hash plain-text password using bcrypt.
    
    WHY USED:
    - Users shouldn't store plain passwords in database
    - Bcrypt is slow (prevents brute force)
    - Bcrypt includes salt (prevents rainbows)
    
    WHAT IT DOES:
    1. Truncates password to 72 bytes (bcrypt limit)
    2. Encodes as UTF-8
    3. Applies bcrypt with 12 salt rounds
    4. Returns hex string
    
    HOW TO USE:
        >>> hash = hash_password("user_password")
        >>> # hash is now: '$2b$12$...' (bcrypt format)
        >>> # Save hash to database, NOT password
    
    SECURITY NOTE:
    - Always compare with verify_password(), never ==
    - 72-byte limit = truncate long passwords
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).hex()
```

### Level 3: Inline Comments (Implementation details)
```python
# WHY: Bcrypt only supports first 72 bytes
# Longer passwords are silently truncated
password = password[:72]

# WHY: UTF-8 encoding required (bcrypt works with bytes)
# Different encodings = different hashes
password_bytes = password.encode('utf-8')

# WHY: 12 salt rounds = ~250ms hash time
# Higher = slower (more security)
# 10 = ~100ms, 15 = ~1s
hash_object = bcrypt.hashpw(password_bytes, bcrypt.gensalt(12))
```

---

## Data Models & Relationships

### User Model
```python
class User(Base):
    __tablename__ = "users"
    
    id: int                           # Unique identifier
    username: str                     # Login name (UNIQUE)
    password_hash: str                # Bcrypt hash (never plain password)
    created_at: datetime              # Account creation time
    books: List["Book"]               # Relationship: user's uploads
    
    # RELATIONSHIPS:
    # One User has Many Books
    # When user deleted: all books deleted (cascade)
```

### Book Model
```python
class Book(Base):
    __tablename__ = "books"
    
    id: int                           # Unique identifier
    user_id: int                      # Foreign key → User
    filename: str                     # Original PDF name
    pdf_content: bytes                # Binary PDF data
    created_at: datetime              # Upload time
    
    # RELATIONSHIPS:
    # Many Books belong to One User
    # user_id must exist in users table
```

### Database Flow
```
Database (SQLite file)
├── users table (rows: usernames, hashes)
└── books table (rows: PDFs, owner IDs)

Python Code
├── User model (represents row)
└── Book model (represents row)

FastAPI
├── Dependency: def get_db() yields Session
├── Query: db.query(User).filter(username=...)
└── Create: db.add(Book(...)); db.commit()
```

---

## API Endpoint Design

Each feature's `routes/` folder contains FastAPI endpoints:

### Auth Routes (`features/auth/routes/`)
```python
@app.post("/api/auth/register")
def register(user: UserCreate):
    """Create new user account"""
    # 1. Validate input (password strength, username unique)
    # 2. Hash password with auth_service.hash_password()
    # 3. Store in database
    # 4. Return JWT token

@app.post("/api/auth/login")  
def login(username: str, password: str):
    """Authenticate user, return token"""
    # 1. Find user by username
    # 2. Verify password with auth_service.verify_password()
    # 3. If correct: return JWT token
    # 4. If wrong: return 401 error

@app.post("/api/auth/logout")
def logout(token: str):
    """Invalidate user's session"""
    # Add token to blacklist
```

### Books Routes (`features/books/routes/`)
```python
@app.post("/api/books/upload")
def upload_pdf(file: UploadFile, user_id: int):
    """Process and index new PDF"""
    # 1. Read uploaded file
    # 2. pdf_loader.load_pdf_binary(file)
    # 3. chunking.split_text(text, chunk_size=500)
    # 4. embeddings.embed_chunks(chunks)
    # 5. vector_store.create_index(embedded)
    # 6. Save to database

@app.get("/api/books/search")
def search(query: str, user_id: int):
    """Semantic search user's documents"""
    # 1. embeddings.embed_text(query)
    # 2. vector_store.search(query_vector, k=5)
    # 3. Return top 5 matches
```

---

## External Services Integration

```
Medi AI Application
│
├─→ SambaNova API
│   └─ For: Generating embeddings (text → vectors)
│   └─ When: During document upload + search
│   └─ Cost: Per-token pricing
│
├─→ Ollama (Local)
│   └─ For: Running LLM locally (privacy)
│   └─ When: Chat responses
│   └─ Cost: Free (local compute)
│
├─→ Tesseract OCR (Local)
│   └─ For: Extracting text from images
│   └─ When: Scanned documents
│   └─ Cost: Free (open source)
│
└─→ Database (SQLite)
    └─ For: Persisting users, PDFs, chat history
    └─ When: Every query, save, update
    └─ Cost: Free (local file)
```

---

## Configuration Management

### Environment Variables (`.env`)
```bash
# ⚠️  Security: Never commit .env to git

# API Keys
SAMBANOVA_API_KEY=your-secret-key-here
SAMBANOVA_BASE_URL=https://api.sambanova.ai/v1

# Database
DATABASE_URL=sqlite:///./database/medi_ai.db

# JWT Security
SECRET_KEY=your-secret-key-change-in-prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# LLM Settings
OLLAMA_BASE_URL=http://localhost:11434
LOCAL_MODEL_NAME=llama2

# Embedding Settings
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Logging
LOG_LEVEL=INFO
```

### Accessing Config in Code
```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SAMBANOVA_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

## Request/Response Flow

### Complete Login Flow
```
FRONTEND sends
└─ POST /api/auth/login
    └─ Body: {"username": "john", "password": "pass123"}

BACKEND processes
├─ 1. Route handler validates input
├─ 2. auth_service.verify_password(input, stored_hash)
├─ 3. Passwords match?
│   ├─ YES: auth_service.create_access_token(user_id)
│   └─ NO: raise HTTPException(401)
└─ 4. Return JWT token

FRONTEND receives
└─ {"access_token": "eyJ0eXAi...", "token_type": "bearer"}

FRONTEND stores
└─ Token in localStorage
└─ Sends in header: "Authorization: Bearer eyJ0eXAi..."

BACKEND validates (next request)
├─ Extract token from Authorization header
└─ auth_service.verify_access_token(token)
    ├─ Check signature valid
    ├─ Check not expired
    └─ Extract user_id
```

### Complete Search Flow
```
FRONTEND sends
└─ POST /api/books/search?query=heart+disease

BACKEND processes
├─ 1. embeddings.embed_text("heart disease")
│   └─ API call to SambaNova → [0.234, 0.891, ...]
├─ 2. vector_store.search(query_vector, k=5)
│   └─ FAISS finds nearest 5 vectors
├─ 3. Retrieve full chunks from database
├─ 4. Rank by relevance (distance score)
└─ 5. Return to frontend

FRONTEND receives
└─ [
     {"id": 1, "text": "Heart disease...", "score": 0.92},
     {"id": 2, "text": "Cardiac issues...", "score": 0.88},
     ...
   ]

FRONTEND displays
└─ Shows results ranked by score
```

---

## Database Queries Examples

### Using SQLAlchemy ORM
```python
from features.shared.services.database_service import get_db
from features.shared.models import User, Book

# Get user by username
user = db.query(User).filter(User.username == "john").first()

# Get all books for user
books = db.query(Book).filter(Book.user_id == user.id).all()

# Create new book
new_book = Book(
    user_id=user.id,
    filename="medical_guide.pdf",
    pdf_content=pdf_bytes
)
db.add(new_book)
db.commit()

# Update user
user.name = "John Doe"
db.commit()

# Delete book
db.delete(book)
db.commit()
```

### Why ORM vs SQL?
| Aspect | ORM (SQLAlchemy) | Raw SQL |
|--------|-----------------|---------|
| SQL Injection | Protected | Vulnerable |
| Code Readability | Clear: `User.username == "x"` | Complex: `SELECT * FROM users WHERE username='x'` |
| Database Portability | Works with SQLite→PostgreSQL | Need to rewrite queries |
| Type Checking | Python IDE autocomplete | No hints |
| Relationships | `.books` navigates to related | Need manual JOINs |

---

## Testing Services

### Unit Test Example
```python
# Test auth service
from features.auth.services.auth_service import hash_password, verify_password

def test_password_hashing():
    """Verify password hashing works correctly"""
    original = "test_password_123"
    
    # Hash it
    hashed = hash_password(original)
    
    # Should verify correct password
    assert verify_password(original, hashed) == True
    
    # Should fail wrong password
    assert verify_password("wrong_password", hashed) == False
    
    # Should fail empty password
    assert verify_password("", hashed) == False

# Run test
pytest backend/features/auth/services/test_auth_service.py
```

### Integration Test (API Level)
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_flow():
    # Register
    register_response = client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "password123"
    })
    assert register_response.status_code == 201
    
    # Login
    login_response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert login_response.status_code == 200
    
    # Should have token
    token = login_response.json()["access_token"]
    assert token is not None
```

---

## Common Tasks Checklist

### 🆕 Adding New Feature (e.g., "feedback")
- [ ] Create folder: `features/feedback/`
- [ ] Create subfolders: `services/`, `models/`, `routes/`, create `README.md`
- [ ] Create `services/feedback_service.py` with comprehensive docstrings
- [ ] Create `models/feedback.py` with Pydantic models
- [ ] Create `routes/feedback_routes.py` with FastAPI endpoints
- [ ] Add imports in `__init__.py` files
- [ ] Write tests in `test_feedback_service.py`
- [ ] Update top-level `README.md` with new feature

### 🆕 Adding New Endpoint (e.g., POST /api/books/favorite)
- [ ] Add function in `features/books/routes/books_routes.py`
- [ ] Write endpoint with FastAPI decorators
- [ ] Add service method if needed
- [ ] Add Pydantic model for request/response
- [ ] Document with docstrings
- [ ] Test with curl or Postman

### 🆕 Adding Database Field (e.g., Book.description)
- [ ] Update model in `features/shared/models/book.py`
- [ ] Create database migration (Alembic)
- [ ] Update service methods to handle field
- [ ] Update API response model
- [ ] Test database query

### 🐛 Debugging Authentication Issue
- [ ] Check token in `Authorization: Bearer <token>` header
- [ ] Verify `auth_service.verify_access_token()` succeeds
- [ ] Check token expiration: `payload['exp'] > datetime.now()`
- [ ] Verify `SECRET_KEY` same as when token created
- [ ] Check user exists in database

---

## Performance Checkpoints

| Component | Metric | Target |
|-----------|--------|--------|
| Password Hashing | Time | 0.3-0.5s (intentionally slow) |
| JWT Verification | Time | <5ms |
| PDF Upload (10MB) | Time | <2s |
| Text Embedding | Time | 1-2 requests/sec (API limited) |
| Semantic Search | Time | <500ms for 1000 documents |
| Database Query | Time | <10ms per query |

---

## Security Checklist

- [ ] Passwords hashed with bcrypt (never plain)
- [ ] JWT tokens signed with SECRET_KEY
- [ ] SQLAlchemy prevents SQL injection
- [ ] Environment variables for secrets (not hardcoded)
- [ ] HTTPS enforced in production
- [ ] User isolation (filter by user_id)
- [ ] Timing-safe password comparison
- [ ] Token expiration (24 hours max)
- [ ] Input validation on all endpoints
- [ ] Rate limiting on auth endpoints
- [ ] Logging for security events
- [ ] CORS configured for frontend domain

---

## Deployment Checklist

- [ ] All services have comprehensive docstrings
- [ ] All tests passing locally
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Indexes created for frequent queries
- [ ] Logs configured and rotating
- [ ] Error monitoring setup (e.g., Sentry)
- [ ] Performance monitoring setup
- [ ] Backup strategy documented
- [ ] Docker image builds successfully
- [ ] API documentation generated (SwaggerUI)
- [ ] Security audit completed

---

## Resources & File Locations

| What | Where | Details |
|------|-------|---------|
| **Auth Examples** | `features/auth/services/auth_service.py` | Password hashing, JWT tokens |
| **Database Setup** | `features/shared/services/database_service.py` | SQLAlchemy models, relationships |
| **PDF Processing** | `features/books/services/pdf_loader_service.py` | Text extraction examples |
| **Embeddings** | `features/books/services/embeddings_service.py` | Vector generation, batch processing |
| **Search** | `features/shared/services/vector_store_service.py` | FAISS indexing, similarity search |
| **API Entry** | `main.py` | FastAPI app initialization |
| **Config** | `.env` | Environment variables |
| **Database** | `database/chroma_db/` | SQLite database file |
| **Feature Docs** | `features/{feature}/README.md` | Feature-specific documentation |

---

## Architecture Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  Displays UI, sends HTTP requests, receives JSON responses      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ HTTP/JSON
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                FASTAPI FRAMEWORK (main.py)                      │
│  Route handler → Validate → Call service → Return JSON          │
├────────────────┬───────────┬──────────────┬──────────────┬──────┤
│  /api/auth/*   │ /api/books│ /api/chat/*  │ /api/dash... │      │
└────────────────┼───────────┼──────────────┼──────────────┘      │
                 │           │              │                      │
         ┌───────▼───────┐ ┌──┴──────────┐ ┌┴────────────────────┐│
         │  Auth Feature │ │ Books Feature│ │ Chat + Dashboard    ││
         │               │ │              │ │                    ││
         │ auth_service  │ │ pdf_loader   │ │ local_llm          ││
         │ JWT tokens    │ │ embeddings   │ │ sambanova_api      ││
         │               │ │ chunking     │ │ cache              ││
         │               │ │ ocr_service  │ │                    ││
         └───────┬───────┘ └──┬───────────┘ └┬────────────────────┘│
                 │            │             │                      │
         ┌───────┴────────────┴─────────────┴──────────────────────┐
         │          SHARED FEATURE (Core Infrastructure)           │
         │                                                          │
         │  ┌──────────────────┐  ┌──────────────────┐            │
         │  │ database_service │  │ vector_store     │            │
         │  │                  │  │ (FAISS)          │            │
         │  │ SQLAlchemy ORM   │  │                  │            │
         │  │ User, Book models│  │ Semantic Search  │            │
         │  └──────────┬───────┘  └────────┬─────────┘            │
         │             │                   │                      │
         │    ┌────────▼──────────────────▼────────┐              │
         │    │      SQLite Database               │              │
         │    │  (users, books, embeddings)        │              │
         │    └─────────────────────────────────────┘              │
         │                                                         │
         │    ┌─────────────────────────────────────────────────┐ │
         │    │   External Services                             │ │
         │    │  - SambaNova API (embeddings)                   │ │
         │    │  - Ollama (local LLM)                           │ │
         │    │  - Tesseract OCR (image text)                   │ │
         │    └─────────────────────────────────────────────────┘ │
         └──────────────────────────────────────────────────────────┘
```

---

## Next Steps for Developers

1. **Understand the Architecture**
   - Read `features/README.md` (30 min)
   - Pick a feature, read its README (15 min)
   - Skim `main.py` to see how routes are registered (10 min)

2. **Explore Core Services**
   - Read `auth_service.py` (understand password security)
   - Read `database_service.py` (understand data models)
   - Read `vector_store_service.py` (understand search)

3. **Run Something**
   - Start dev server: `python main.py`
   - Test endpoint: `curl http://localhost:8000/api/auth/login`
   - Check logs for errors

4. **Write Code**
   - Add endpoint to existing feature
   - Add service method
   - Write tests
   - Update documentation

---

**Architecture Type:** Feature-Based Modular  
**Framework:** FastAPI  
**Database:** SQLAlchemy + SQLite/PostgreSQL  
**Search:** FAISS + Semantic Embeddings  
**Documentation:** WHY + WHAT + HOW for all code  

Version: 1.0 | Last Updated: April 2026 | Status: ✅ Complete
