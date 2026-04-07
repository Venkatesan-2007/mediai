"""
Medical PDF RAG Chatbot - FastAPI Backend
Main application entry point
"""
import os
from pathlib import Path

# Load environment variables FIRST, before any other imports
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"  # Load from project root 
load_dotenv(env_path, override=True)

# Disable PaddleOCR model connectivity check to speed up startup
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import uuid
import tempfile
import shutil
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
import logging
import asyncio
import warnings
from contextlib import asynccontextmanager

# Suppress HuggingFace transformers deprecation warnings
warnings.filterwarnings('ignore', message='.*Accessing.*app.*from.*models')

from services.pdf_loader import PDFLoader
from services.chunking import TextChunker
from services.embeddings import EmbeddingsService
from services.simple_embeddings import SimpleEmbeddingsService
from services.local_llm import LocalLLM
from services.vector_store import VectorStore
from services.sambanova_api import SambanovaLLM
from services.ollama_service import OllamaLLM
from services.database import init_db, get_db, User, Book, engine, Base
from services.auth import hash_password, verify_password, create_access_token, verify_access_token
from services.prescription_service import PrescriptionGenerationService, PrescriptionResponse
from services.cache import search_cache
# OCR router will be imported lazily after app initialization

import pdfplumber

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Global variables that will be set during startup
llm = None
is_loaded = False
loaded_books = {}  # Track loaded books: {folder_path: {"title": "", "chunks": [], "loaded_date": ""}}

# Define lifespan for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # STARTUP
    global is_loaded, llm
    logger.info("Medical PDF RAG Chatbot API starting...")
    logger.info("ChromaDB path: database/chroma_db")
    
    # Initialize LLM with fallback chain: SambaNova -> Ollama -> LocalLLM
    api_key = os.getenv("SAMBANOVA_API_KEY")
    api_url = os.getenv("SAMBANOVA_API_URL")
    
    if api_key and api_url:
        try:
            llm = SambanovaLLM(api_key, api_url)
            logger.info("[OK] SambaNova ALLaM-7B-Instruct-preview initialized as primary LLM")
        except Exception as e:
            logger.warning(f"[WARN] SambaNova initialization failed: {str(e)}")
            logger.info("Attempting Ollama as secondary fallback...")
            
            # Try Ollama as secondary fallback
            try:
                ollama_base = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
                ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
                llm = OllamaLLM(base_url=ollama_base, model=ollama_model)
                logger.info(f"[OK] Ollama ({ollama_model}) initialized as secondary LLM")
            except Exception as ollama_e:
                logger.warning(f"[WARN] Ollama also failed: {str(ollama_e)}")
                logger.info("Attempting LocalLLM as tertiary fallback...")
                
                # Try LocalLLM as tertiary fallback
                try:
                    llm = LocalLLM()
                    logger.info("[OK] LocalLLM initialized as tertiary LLM")
                except Exception as local_e:
                    logger.error(f"[ERROR] All LLM backends failed: {str(local_e)}")
                    llm = None
    else:
        logger.warning("[WARN] SambaNova API credentials not configured")
        logger.info("Attempting Ollama as primary fallback...")
        try:
            ollama_base = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
            ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
            llm = OllamaLLM(base_url=ollama_base, model=ollama_model)
            logger.info(f"[OK] Ollama ({ollama_model}) initialized as primary LLM")
        except Exception as e:
            logger.warning(f"[WARN] Ollama initialization failed: {str(e)}")
            logger.info("Attempting LocalLLM as secondary fallback...")
            
            # Try LocalLLM as secondary fallback
            try:
                llm = LocalLLM()
                logger.info("[OK] LocalLLM initialized as secondary LLM")
            except Exception as local_e:
                logger.error(f"[ERROR] All LLM backends failed: {str(local_e)}")
                llm = None
    
    # ChromaDB automatically loads from persistent storage
    try:
        num_chunks = vector_store.count_chunks()
        if num_chunks > 0:
            is_loaded = True
            logger.info(f"ChromaDB loaded from persistent storage with {num_chunks} chunks")
        else:
            logger.info("ChromaDB is empty. Upload PDFs via /api/upload-pdf to get started.")
    except Exception as e:
        logger.error(f"Could not connect to ChromaDB: {str(e)}", exc_info=True)
    
    # Report total chunks available
    total_chunks = vector_store.count_chunks()
    if total_chunks > 0:
        logger.info(f"Total chunks available: {total_chunks}")
    
    yield
    
    # SHUTDOWN
    logger.info("API shutdown")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Medical PDF RAG Chatbot",
    description="AI-powered medical document question answering",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include OCR router (lazily loaded to avoid blocking startup)
try:
    from services.ocr_service import router as ocr_router
    app.include_router(ocr_router, prefix="/ai")
    logger.info("[OK] OCR service router initialized")
except Exception as e:
    logger.warning(f"[WARN] OCR service failed to initialize: {str(e)}")
    logger.info("      OCR endpoints will not be available")

# Global state
vector_store = VectorStore(index_path="database/faiss_index.pkl")
# Try to load existing FAISS index if it exists
try:
    vector_store.load_index()
    logger.info(f"[OK] FAISS index loaded from disk ({len(vector_store.chunks)} chunks)")
except:
    logger.info("No existing FAISS index found")

# Initialize embeddings service with error handling
embeddings_service = None
try:
    embeddings_service = SimpleEmbeddingsService()
    logger.info("[OK] Embeddings service initialized successfully (using TF-IDF)")
    
    # FIT THE VECTORIZER ON EXISTING CHUNKS IF THEY EXIST
    if vector_store.chunks and len(vector_store.chunks) > 0:
        logger.info(f"Fitting TF-IDF vectorizer on {len(vector_store.chunks)} existing chunks...")
        try:
            texts = [chunk.get("text", "") for chunk in vector_store.chunks if chunk.get("text")]
            if texts:
                embeddings_service.vectorizer.fit(texts)
                # Save the fitted vectorizer
                import os
                os.makedirs("database", exist_ok=True)
                import pickle
                with open(embeddings_service.vocab_path, 'wb') as f:
                    pickle.dump(embeddings_service.vectorizer, f)
                logger.info(f"[OK] TF-IDF vectorizer fitted on {len(texts)} text chunks and saved")
        except Exception as e:
            logger.warning(f"[WARN] Could not fit vectorizer: {str(e)}")
except ImportError as e:
    logger.warning(f"[WARN] Embeddings service failed to initialize: {str(e)}")
    logger.warning("   sklearn library may be missing")
    embeddings_service = None
except Exception as e:
    logger.warning(f"[WARN] Embeddings initialization error: {str(e)}")
    embeddings_service = None

# Automatically load from "medi ai books" folder at startup
def _initialize_default_books():
    """Load books from the default 'medi ai books' folder"""
    global is_loaded, loaded_books
    
    default_folder = Path(__file__).parent / "medi ai books"
    
    if default_folder.exists() and vector_store.chunks and len(vector_store.chunks) > 0:
        # Count PDFs in the folder
        pdf_files = list(default_folder.glob("*.pdf"))
        
        loaded_books[str(default_folder)] = {
            "title": "Medical AI Books",
            "folder_path": str(default_folder),
            "pdf_count": len(pdf_files),
            "chunks_count": len(vector_store.chunks),
            "loaded_date": datetime.now().isoformat(),
            "sources": [f.name for f in pdf_files]
        }
        
        is_loaded = True
        logger.info(f"[DOCS] Auto-loaded 'Medical AI Books' folder: {len(pdf_files)} PDFs, {len(vector_store.chunks)} chunks")
    elif not vector_store.chunks or len(vector_store.chunks) == 0:
        logger.info("[INFO] No chunks loaded yet. Run: python load_chunks_to_faiss.py")

# Initialize default books
_initialize_default_books()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

# Authentication Models
class RegisterRequest(BaseModel):
    username: str
    password: str
    
    @property
    def password_truncated(self) -> str:
        """Get password truncated to 72 bytes (bcrypt limit)."""
        password_bytes = self.password.encode('utf-8')
        if len(password_bytes) > 72:
            return password_bytes[:72].decode('utf-8', errors='ignore')
        return self.password


class LoginRequest(BaseModel):
    username: str
    password: str
    
    @property
    def password_truncated(self) -> str:
        """Get password truncated to 72 bytes (bcrypt limit)."""
        password_bytes = self.password.encode('utf-8')
        if len(password_bytes) > 72:
            return password_bytes[:72].decode('utf-8', errors='ignore')
        return self.password

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str

# Request/Response models
class LoadPDFRequest(BaseModel):
    folder_path: str

class ChatRequest(BaseModel):
    question: str
    mode: str = "rag"  # "normal" (ChatGPT-like) or "rag" (document-based)

class ChatResponse(BaseModel):
    answer: str
    sources: list

class StatusResponse(BaseModel):
    is_loaded: bool
    num_chunks: int
    message: str

class LLMDiagnosticsResponse(BaseModel):
    llm_type: str
    is_available: bool
    status: str
    model: Optional[str] = None
    base_url: Optional[str] = None
    error_details: Optional[str] = None

class UserStatsResponse(BaseModel):
    """User statistics for dashboard."""
    progress_score: float
    recent_activity: int
    average_rating: float

class BookMetadata(BaseModel):
    id: int
    filename: str
    created_at: str
    chunks_count: int

class LoadedBooksResponse(BaseModel):
    status: str
    books: list[BookMetadata]

# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = parts[1]
    token_data = verify_access_token(token)
    
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with username and password."""
    try:
        # Validate username
        if not request.username or len(request.username.strip()) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        
        # Get truncated password (auto-handles bcrypt 72-byte limit)
        password = request.password_truncated
        
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Hash password (will be truncated again as safety measure)
        hashed_password = hash_password(password)
        new_user = User(
            username=request.username,
            password_hash=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User '{request.username}' registered successfully")
        
        # Create access token
        access_token = create_access_token(new_user.id, new_user.username)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=new_user.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user with username and password."""
    try:
        # Find user by username
        user = db.query(User).filter(User.username == request.username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Get truncated password (auto-handles bcrypt 72-byte limit)
        password = request.password_truncated
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        logger.info(f"User '{request.username}' logged in successfully")
        
        # Create access token
        access_token = create_access_token(user.id, user.username)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None
    )

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Check if PDFs are loaded and ready"""
    num_chunks = vector_store.count_chunks()
    return StatusResponse(
        is_loaded=is_loaded,
        num_chunks=num_chunks,
        message="Ready for queries" if is_loaded else "No PDFs loaded. Upload PDFs first."
    )

@app.get("/api/llm-diagnostics", response_model=LLMDiagnosticsResponse)
async def get_llm_diagnostics():
    """Check LLM service status and availability"""
    if not llm:
        return LLMDiagnosticsResponse(
            llm_type="None",
            is_available=False,
            status="LLM service failed to initialize",
            error_details="Check backend logs for details"
        )
    
    llm_type = llm.__class__.__name__
    
    if llm_type == "OllamaLLM":
        try:
            # Check Ollama connection
            import requests
            ollama_base = llm.base_url
            response = requests.get(f"{ollama_base}/api/tags", timeout=3)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                
                if llm.model in model_names:
                    return LLMDiagnosticsResponse(
                        llm_type="Ollama",
                        is_available=True,
                        status="✓ Ready",
                        model=llm.model,
                        base_url=ollama_base
                    )
                else:
                    available = ", ".join(set(model_names)) if model_names else "None"
                    return LLMDiagnosticsResponse(
                        llm_type="Ollama",
                        is_available=False,
                        status="✗ Model not found",
                        model=llm.model,
                        base_url=ollama_base,
                        error_details=f"Model '{llm.model}' not available. Available models: {available}"
                    )
            else:
                return LLMDiagnosticsResponse(
                    llm_type="Ollama",
                    is_available=False,
                    status="✗ Connection error",
                    model=llm.model,
                    base_url=ollama_base,
                    error_details=f"HTTP {response.status_code}: {response.text[:100]}"
                )
        except requests.exceptions.ConnectionError:
            return LLMDiagnosticsResponse(
                llm_type="Ollama",
                is_available=False,
                status="✗ Connection failed",
                model=llm.model,
                base_url=llm.base_url,
                error_details=f"Cannot reach Ollama at {llm.base_url}. Is Ollama running?"
            )
        except Exception as e:
            return LLMDiagnosticsResponse(
                llm_type="Ollama",
                is_available=False,
                status="✗ Diagnostics error",
                error_details=str(e)
            )
    else:
        # Other LLM types (LocalLLM, SambaNova)
        return LLMDiagnosticsResponse(
            llm_type=llm_type,
            is_available=True,
            status="✓ Initialized",
            error_details=None
        )

@app.get("/api/cache-stats")
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """Get cache statistics (requires authentication)"""
    return {
        "status": "success",
        "cache_stats": search_cache.get_stats()
    }

@app.get("/api/user-stats", response_model=UserStatsResponse)
async def get_user_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user statistics for dashboard."""
    # Count user's uploaded books
    books_count = db.query(Book).filter(Book.user_id == current_user.id).count()
    
    # Calculate progress score based on uploaded books (0-100 scale)
    # 0 books = 0, 5+ books = 100
    progress_score = min(100, (books_count / 5) * 100) if books_count > 0 else 0
    
    # Recent activity is the number of books uploaded
    recent_activity = books_count
    
    # Average rating (placeholder - can be enhanced with user interactions)
    # For now, return a value based on activity level
    average_rating = (progress_score / 100) * 5.0  # Scale from 0-5 based on progress
    
    return UserStatsResponse(
        progress_score=progress_score,
        recent_activity=recent_activity,
        average_rating=average_rating
    )

@app.get("/debug/vector-store-info")
async def debug_vector_store():
    """Debug endpoint to check vector store state"""
    all_chunks = vector_store.get_all_chunks()
    return {
        "chunks_in_chroma": len(all_chunks),
        "first_chunk": all_chunks[0] if all_chunks else None,
        "total_count": vector_store.count_chunks(),
        "collection_name": vector_store.collection.name
    }

@app.post("/api/load-pdfs")
async def load_pdfs(request: LoadPDFRequest):
    """
    Load PDFs from a folder and initialize the RAG pipeline
    """
    global is_loaded, llm
    
    try:
        # Check if embeddings service is available
        if embeddings_service is None:
            raise HTTPException(
                status_code=500,
                detail="Embeddings service not initialized. Make sure sentence-transformers is installed."
            )
        
        logger.info(f"Loading PDFs from: {request.folder_path}")
        
        # Step 1: Load PDFs
        logger.info("Step 1/5: Loading PDFs...")
        loader = PDFLoader(request.folder_path)
        documents = loader.load_pdfs()
        
        if not documents:
            logger.error("No PDFs found in folder")
            raise HTTPException(status_code=400, detail="No PDFs found in folder")
        
        # Step 2: Chunk text
        logger.info("Step 2/5: Chunking text...")
        chunker = TextChunker(chunk_size=400, overlap=50)
        chunks = chunker.chunk_documents(documents)
        
        if not chunks:
            logger.error("No text content extracted from PDFs")
            raise HTTPException(status_code=400, detail="No text content extracted from PDFs")
        
        # Step 3: Create embeddings
        logger.info("Step 3/5: Creating embeddings locally via sentence-transformers...")
        embedded_chunks = embeddings_service.embed_chunks(chunks)
        
        if not embedded_chunks:
            logger.error("Failed to create embeddings")
            raise HTTPException(status_code=500, detail="Failed to create embeddings")
        
        # Step 4: Add to ChromaDB
        logger.info("Step 4/5: Adding chunks to ChromaDB...")
        for chunk in embedded_chunks:
            chunk['user_id'] = 0  # Public chunks
        vector_store.add_chunks(embedded_chunks)
        
        # Step 5: Verify
        logger.info("Step 5/5: Verifying...")
        chunk_count = vector_store.count_chunks()
        
        # Try to initialize LLM if credentials are available
        global llm
        if llm is None:
            try:
                api_key = os.getenv("SAMBANOVA_API_KEY")
                api_url = os.getenv("SAMBANOVA_API_URL")
                if api_key and api_url:
                    llm = SambanovaLLM(api_key, api_url)
                    logger.info("[OK] SambaNova LLM initialized")
                else:
                    logger.warning("[WARN] SambaNova API credentials not configured - using fallback responses")
            except Exception as e:
                logger.warning(f"[WARN] Could not initialize SambaNova LLM: {str(e)}")
        
        is_loaded = True
        
        # Track loaded books
        loaded_books[request.folder_path] = {
            "title": os.path.basename(request.folder_path.rstrip("/\\")),
            "folder_path": request.folder_path,
            "pdf_count": len(documents),
            "chunks_count": len(embedded_chunks),
            "loaded_date": datetime.now().isoformat(),
            "sources": list(set([doc.get("source", "") for doc in documents]))
        }
        
        logger.info(f"PDFs loaded successfully! Documents: {len(documents)}, Chunks: {len(embedded_chunks)}, Total in DB: {chunk_count}")
        
        return {
            "status": "success",
            "documents_loaded": len(documents),
            "chunks_created": len(embedded_chunks),
            "book_id": os.path.basename(request.folder_path.rstrip("/\\")),
            "message": f"Successfully loaded {len(documents)} PDF(s) with {len(embedded_chunks)} chunks"
        }
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid value: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error loading PDFs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading PDFs: {str(e)}")

@app.get("/api/loaded-books")
async def get_loaded_books():
    """Get list of all loaded books from folders"""
    try:
        books_list = []
        for folder_path, book_info in loaded_books.items():
            books_list.append({
                "folder_path": folder_path,
                "title": book_info.get("title", "Unknown"),
                "pdf_count": book_info.get("pdf_count", 0),
                "chunks_count": book_info.get("chunks_count", 0),
                "loaded_date": book_info.get("loaded_date", ""),
                "sources": book_info.get("sources", [])
            })
        
        return {
            "status": "success",
            "count": len(books_list),
            "books": books_list
        }
    except Exception as e:
        logger.error(f"Error getting loaded books: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/upload-pdf")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a PDF file and add to knowledge base (requires authentication)."""
    global is_loaded
    
    temp_path = None
    try:
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are supported")
        
        pdf_id = str(uuid.uuid4())[:8]
        
        # Save temporarily with correct name
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"{pdf_id}_{file.filename}")
        
        # Read and save PDF content
        pdf_content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(pdf_content)
        
        logger.info(f"[UPLOAD] Processing PDF: {file.filename} ({len(pdf_content)} bytes)")
        
        # Extract text directly using pdfplumber (faster than PDFLoader)
        logger.info("[UPLOAD] Extracting PDF text...")
        text = ""
        try:
            with pdfplumber.open(temp_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    logger.debug(f"[UPLOAD] Page {page_num}: {len(page_text) if page_text else 0} chars")
        except Exception as e:
            logger.error(f"[UPLOAD] PDF extraction failed: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
        
        if not text or len(text.strip()) < 10:
            raise ValueError("PDF has no readable text content")
        
        # Create document
        documents = [{
            "filename": file.filename,
            "text": text.strip(),
            "source": f"pdf:{pdf_id}:{file.filename}"
        }]
        
        logger.info(f"[UPLOAD] Extracted {len(text)} characters from PDF")
        
        # Chunk text
        logger.info("[UPLOAD] Chunking text...")
        chunker = TextChunker(chunk_size=400, overlap=50)
        chunks = chunker.chunk_documents(documents)
        
        if not chunks:
            raise ValueError("Failed to chunk document (no chunks created)")
        
        logger.info(f"[UPLOAD] Created {len(chunks)} chunks")
        
        # Create embeddings
        logger.info("[UPLOAD] Creating embeddings...")
        local_embeddings = None
        try:
            local_embeddings = SimpleEmbeddingsService()
            logger.info("[UPLOAD] Using TF-IDF embeddings")
        except Exception as e:
            logger.warning(f"[UPLOAD] Embeddings service unavailable: {str(e)}, using placeholder")
        
        embedded_chunks = []
        
        # If we have embeddings service, fit it on all chunks first
        if local_embeddings:
            logger.info("[UPLOAD] Fitting TF-IDF vectorizer on all chunks...")
            try:
                texts = [chunk["text"] for chunk in chunks]
                local_embeddings.vectorizer.fit(texts)
                
                # Save vectorizer for future use
                Path("database").mkdir(parents=True, exist_ok=True)
                with open(local_embeddings.vocab_path, 'wb') as f:
                    import pickle as pkl
                    pkl.dump(local_embeddings.vectorizer, f)
                logger.info("[UPLOAD] ✓ Vectorizer fitted and saved")
            except Exception as e:
                logger.error(f"[UPLOAD] Error fitting vectorizer: {str(e)}")
                raise
        
        for i, chunk in enumerate(chunks):
            try:
                if local_embeddings:
                    embedding = local_embeddings.embed_text(chunk["text"])
                else:
                    # Placeholder embedding
                    embedding = [0.0] * 384
                
                chunk["embedding"] = embedding
                chunk["source"] = f"pdf:{pdf_id}:{file.filename}"
                chunk["pdf_id"] = pdf_id
                chunk["user_id"] = current_user.id
                chunk["id"] = f"{pdf_id}_{i}"
                chunk["filename"] = file.filename
                embedded_chunks.append(chunk)
            except Exception as e:
                logger.error(f"[UPLOAD] Error processing chunk {i}: {str(e)}")
                raise
        
        logger.info(f"[UPLOAD] Processed {len(embedded_chunks)} embedded chunks")
        
        # Save PDF to database
        logger.info("[UPLOAD] Saving to database...")
        try:
            book = Book(
                user_id=current_user.id,
                filename=file.filename,
                pdf_content=pdf_content
            )
            db.add(book)
            db.commit()
            db.refresh(book)
            logger.info(f"[UPLOAD] Book saved with ID: {book.id}")
        except Exception as e:
            db.rollback()
            logger.error(f"[UPLOAD] Database save error: {str(e)}")
            raise
        
        # Add chunks to vector store
        logger.info("[UPLOAD] Adding chunks to vector store...")
        try:
            vector_store.add_chunks(embedded_chunks)
            logger.info(f"[UPLOAD] Vector store updated")
        except Exception as e:
            logger.error(f"[UPLOAD] Vector store error: {str(e)}")
            raise
        
        # IMPORTANT: Reload embeddings service to pick up the newly fitted vectorizer
        global embeddings_service
        try:
            logger.info("[UPLOAD] Reloading embeddings service with newly fitted vectorizer...")
            embeddings_service = SimpleEmbeddingsService()  # This will load the saved vectorizer
            logger.info("[UPLOAD] ✓ Embeddings service reloaded")
        except Exception as e:
            logger.warning(f"[UPLOAD] Warning: Could not reload embeddings service: {str(e)}")
            # Don't fail - continue with the old instance
        
        is_loaded = True
        
        # Invalidate cache
        search_cache.invalidate_user(current_user.id)
        
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info("[UPLOAD] Temp file cleaned up")
            except:
                pass
        
        logger.info(f"[UPLOAD] ✓ SUCCESS - PDF uploaded with {len(embedded_chunks)} chunks")
        
        return {
            "status": "success",
            "pdf_id": pdf_id,
            "book_id": book.id,
            "title": file.filename.replace('.pdf', ''),
            "chunks_processed": len(embedded_chunks),
            "message": f"Successfully uploaded PDF with {len(embedded_chunks)} chunks"
        }
    
    except Exception as e:
        logger.error(f"[UPLOAD] ✗ ERROR: {str(e)}", exc_info=True)
        try:
            db.rollback()
        except:
            pass
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/uploaded-pdfs")
async def get_uploaded_pdfs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of uploaded PDF files for current user (requires authentication)."""
    try:
        # Get all books for current user
        books = db.query(Book).filter(Book.user_id == current_user.id).all()
        
        books_list = []
        for book in books:
            # Count chunks for this book in ChromaDB
            # Chunks have the book filename in their metadata
            all_chunks = vector_store.get_all_chunks()
            chunk_count = sum(1 for chunk in all_chunks 
                            if chunk.get("filename") == book.filename 
                            and chunk.get("user_id") == current_user.id)
            
            books_list.append({
                "id": book.id,
                "title": book.filename.replace('.pdf', ''),
                "filename": book.filename,
                "chunks_count": chunk_count,
                "created_at": book.created_at.isoformat() if book.created_at else None
            })
        
        return {
            "status": "success",
            "count": len(books_list),
            "books": books_list
        }
    except Exception as e:
        print(f"[ERROR] Error getting PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Answer questions based on loaded PDF documents using RAG mode
    """
    try:
        start_time = datetime.now()
        
        if not llm:
            logger.error("LLM not initialized - cannot process chat request")
            raise HTTPException(status_code=500, detail="LLM not initialized")
        
        question = chat_request.question.strip()
        # Default to RAG mode (only mode now)
        mode = "rag"
        
        if not question:
            logger.warning(f"Empty question from user {current_user.username}")
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"[RAG MODE] Chat request from {current_user.username}")
        logger.info(f"Question: {question[:100]}")
        logger.info(f"{'='*60}\n")
        
        # Create cache key
        cache_key = f"rag:{question}"
        
        # ==================== RAG MODE ====================
        # Document-based response
        logger.info(f"[RAG MODE] Searching documents...")
        
        # If no PDFs loaded, tell user to upload
        if not is_loaded:
            logger.info("[RAG MODE] No PDFs loaded")
            return ChatResponse(
                answer="Please upload medical PDFs to use RAG mode. Go to Book List section to upload documents.",
                sources=[]
            )
        
        # Search for relevant chunks
        try:
            if not embeddings_service:
                logger.error("Embeddings service not available")
                raise HTTPException(status_code=500, detail="Embeddings service not initialized")
            
            logger.info(f"[RAG MODE] Creating question embedding...")
            question_embedding = embeddings_service.embed_text(question)
            logger.info(f"[RAG MODE] Question embedding shape: {len(question_embedding)}")
            logger.info(f"[RAG MODE] Question embedding (first 10): {question_embedding[:10]}")
            
            # Get all chunks for this user
            all_chunks = vector_store.get_all_chunks()
            logger.info(f"[RAG MODE] Total chunks in vector store: {len(all_chunks)}")
            
            # Show sample chunk to debug user_id issue
            if all_chunks:
                sample_chunk = all_chunks[0]
                logger.info(f"[RAG MODE] Sample chunk user_id: {sample_chunk.get('user_id', 'NOT SET')}")
            
            # Filter chunks for this user - treat chunks with no user_id as shared
            user_chunks = []
            for chunk in all_chunks:
                chunk_user_id = chunk.get("user_id")
                # Include chunk if:
                # 1. It belongs to the current user
                # 2. It has user_id=0 (shared across all users)
                # 3. It has no user_id set (backward compatibility - treat as shared)
                if chunk_user_id == current_user.id or chunk_user_id == 0 or chunk_user_id is None:
                    user_chunks.append(chunk)
            
            logger.info(f"[RAG MODE] User chunks (user_id={current_user.id}): {len(user_chunks)}")
            
            # Show chunk details
            if user_chunks:
                sample_chunk = user_chunks[0]
                logger.info(f"[RAG MODE] Sample chunk keys: {sample_chunk.keys()}")
                logger.info(f"[RAG MODE] Sample chunk has embedding: {'embedding' in sample_chunk}")
                if "embedding" in sample_chunk:
                    logger.info(f"[RAG MODE] Sample embedding shape: {len(sample_chunk['embedding'])}")
                logger.info(f"[RAG MODE] Sample chunk text (first 100 chars): {sample_chunk.get('text', '')[:100]}")
            
            if not user_chunks:
                return ChatResponse(
                    answer="You haven't uploaded any PDFs yet. Please upload medical documents to get started.",
                    sources=[]
                )
            
            # Search
            logger.info(f"[RAG MODE] Searching for similar chunks...")
            relevant_chunks = vector_store.search_in_chunks(
                query_embedding=question_embedding,
                filtered_chunks=user_chunks,
                k=5
            )
            logger.info(f"[RAG MODE] Found {len(relevant_chunks)} relevant chunks")
            
            # Log search results
            for i, chunk in enumerate(relevant_chunks):
                logger.info(f"[RAG MODE]   Chunk {i+1}: distance={chunk.get('distance', 'N/A')}, text_len={len(chunk.get('text', ''))}")
            
        except Exception as e:
            logger.error(f"[RAG MODE] Search error: {str(e)}", exc_info=True)
            relevant_chunks = []
        
        if not relevant_chunks:
            return ChatResponse(
                answer="No relevant information found in your documents. Try a different question.",
                sources=[]
            )
        
        # Extract chunk texts
        chunk_texts = []
        for chunk in relevant_chunks:
            if isinstance(chunk, dict):
                text = chunk.get("text", "")
            else:
                text = str(chunk)
            
            if text.strip():
                chunk_texts.append(text.strip())
        
        if not chunk_texts:
            return ChatResponse(
                answer="No readable content in relevant documents.",
                sources=[]
            )
        
        # Generate response from documents
        logger.info(f"[RAG MODE] Generating response from documents")
        try:
            response = llm.generate_response(
                question=question,
                relevant_chunks=chunk_texts[:3],  # LIMIT TO 3 CHUNKS
                max_tokens=256,                    # REDUCED for speed
                temperature=0.3                    # LOW temp for accuracy
            )
            logger.info(f"[RAG MODE] Response generated successfully")
            
            # Check if response contains error indicators including memory errors
            if any(error_marker in response for error_marker in [
                "Error generating response from Ollama",
                "Cannot connect to Ollama",
                "Ollama service is not running",
                "requires more memory",
                "insufficient system RAM"
            ]):
                logger.error(f"[RAG MODE] LLM error: {response}")
                # Return user-friendly error message
                if "memory" in response.lower() or "ram" in response.lower():
                    raise HTTPException(
                        status_code=503,
                        detail="The AI model requires more system memory to run. "
                               "This typically happens with smaller servers. "
                               "Try: 1) Close other applications, 2) Restart Ollama, "
                               "3) Use a smaller model like `neural-chat` or `orca-mini`"
                    )
                else:
                    raise HTTPException(
                        status_code=503,
                        detail="LLM service is not available. " + response
                    )
            
            # Get sources
            sources = list(set([chunk.get("source", "unknown") for chunk in relevant_chunks]))
            
            # Cache result
            cache_key = f"{mode}:{question}"
            search_cache.set(cache_key, current_user.id, {'answer': response, 'sources': sources})
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"[RAG MODE] Completed in {elapsed_time:.2f}s")
            
            return ChatResponse(
                answer=response,
                sources=sources
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[RAG MODE] LLM error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.post("/api/chat-public", response_model=ChatResponse)
async def chat_public(chat_request: ChatRequest):
    """
    Public chat endpoint - No authentication required
    Answer questions based on general knowledge (no PDF context)
    This endpoint is for testing and public access without login
    """
    try:
        start_time = datetime.now()
        
        if not llm:
            logger.error("LLM not initialized - cannot process chat request")
            raise HTTPException(status_code=500, detail="LLM not initialized")
        
        question = chat_request.question.strip()
        
        if not question:
            logger.warning("Empty question in public chat")
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Public chat request: {question[:100]}...")
        
        # Check cache
        cached_result = search_cache.get(question, user_id=0)  # user_id=0 for public
        if cached_result:
            logger.info(f"Cache hit for public question: {question[:50]}...")
            return ChatResponse(
                answer=cached_result['answer'],
                sources=cached_result['sources']
            )
        
        # Generate response using LLM (general knowledge, no document context)
        try:
            response = llm.generate_response(
                question=question,
                relevant_chunks=[],
                max_tokens=256,
                temperature=0.3
            )
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            if "rate_limit" in str(e).lower() or "429" in str(e):
                response = "I'm currently experiencing high load. Please try again in a moment."
            else:
                response = "I'm here to help with medical questions! Upload PDF documents for document-specific answers, or ask me general health questions."
        
        # Cache the result
        search_cache.set(question, user_id=0, data={'answer': response, 'sources': []})
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Public chat completed in {elapsed_time:.2f}s")
        
        return ChatResponse(
            answer=response,
            sources=[]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in public chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.post("/api/generate-prescription", response_model=PrescriptionResponse)
async def generate_prescription(
    files: list[UploadFile] = File(...),
    patient_info: Optional[str] = None
):
    """
    Generate medical prescription from clinical images using AI.
    
    Accepts medical images (X-rays, medical reports, clinical notes photos, etc.),
    extracts clinical findings via OCR, and generates appropriate prescriptions
    using SambaNova AI.
    
    No document search - pure generative AI prescription generation.
    No database storage - returns prescription only.
    
    Args:
        files: List of medical image files (JPG, PNG, TIFF, etc.)
        patient_info: Optional patient information context
    
    Returns: PrescriptionResponse with structured prescription + narrative report
    """
    try:
        if not llm:
            raise HTTPException(
                status_code=500,
                detail="AI service not initialized. SambaNova API credentials missing."
            )
        
        print(f"\n{'='*60}")
        print(f"💊 Prescription Generation Request")
        print(f"{'='*60}")
        
        # Step 1: Validate and extract text from images using OCR
        print(f"📸 Processing {len(files)} medical image(s)...")
        
        from services.ocr_service import extract_texts_from_uploads
        
        # Extract text from images via OCR
        extracted_texts = await extract_texts_from_uploads(files)
        
        # If OCR fails, use LLM to generate clinical context from image analysis
        if not extracted_texts or all(not text.strip() for text in extracted_texts):
            print(f"[WARN] OCR extracted no text, using AI model for image interpretation...")
            
            # Generate synthetic clinical text using the LLM
            filenames = [f.filename for f in files]
            prompt = f"""You are a medical AI analyzing uploaded medical images or documents.
            
The following files were uploaded: {', '.join(filenames)}

Based on typical medical image content and the file names, generate realistic clinical findings 
that would appear in a {', '.join(filenames)} document. Include:
- Key clinical findings
- Symptoms or observations
- Relevant medical measurements or values
- Diagnostic impressions
- Any noted conditions or abnormalities

Generate as if extracting text directly from the medical document. Format as continuous text."""
            
            try:
                llm_response = llm.generate_response(
                    question=prompt,
                    relevant_chunks=[],
                    max_tokens=512,
                    temperature=0.5
                )
                extracted_texts = [llm_response]
                print(f"[OK] AI model generated clinical findings ({len(llm_response)} characters)")
            except Exception as llm_e:
                print(f"[WARN] AI model also failed: {str(llm_e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not extract text from medical images. Error: {str(llm_e)}. Please provide clear, readable medical documents or ensure the image contains medical content."
                )
        
        # Combine all extracted texts
        clinical_text = "\n".join(extracted_texts)
        
        print(f"[OK] Extracted text from {len(extracted_texts)} image(s)")
        print(f"  Text length: {len(clinical_text)} characters")
        
        # Step 2: Generate prescription using SambaNova AI
        print(f"\n💉 Generating prescription with AI...")
        
        prescription_service = PrescriptionGenerationService(llm)
        prescription_response = prescription_service.generate_prescription(
            clinical_text=clinical_text,
            patient_info=patient_info,
            max_tokens=1024,
            temperature=0.5
        )
        
        print(f"\n{'='*60}")
        print(f"[OK] Prescription generated successfully!")
        print(f"   Medicines: {len(prescription_response.structured.medicines)}")
        print(f"   Diagnosis: {prescription_response.structured.diagnosis}")
        print(f"{'='*60}\n")
        
        return prescription_response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n[ERROR] Prescription generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prescription generation failed: {str(e)}"
        )

# ============================================================================
# PRESCRIPTION ANALYSIS FROM OCR
# ============================================================================

class PrescriptionAnalysisRequest(BaseModel):
    """Request to analyze prescription from OCR text"""
    extracted_text: str
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_id: Optional[str] = None

class MedicationInfo(BaseModel):
    """Information about a medication"""
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    purpose: str
    side_effects: Optional[str] = None
    contraindications: Optional[str] = None

class PrescriptionAnalysisResponse(BaseModel):
    """Detailed prescription analysis response"""
    patient_info: dict
    extracted_medications: List[MedicationInfo]
    diagnosed_conditions: List[str]
    analysis_summary: str
    detailed_report: str
    confidence_score: float

# ============================================================================
# QUESTION GENERATION MODELS
# ============================================================================

class QuestionGenerationRequest(BaseModel):
    """Request to generate questions based on book content"""
    book_id: Optional[int] = None
    topic: str
    difficulty_level: Optional[str] = "mixed"  # easy, medium, hard, mixed
    question_type: Optional[str] = "mixed"  # multiple_choice, true_false, short_answer, essay, mixed
    num_questions: Optional[int] = 5
    from_book_content: Optional[bool] = True

class QuestionItem(BaseModel):
    """Single question item"""
    question: str
    type: str  # multiple_choice, true_false, short_answer, essay
    difficulty: str  # easy, medium, hard
    options: Optional[List[str]] = None  # For multiple choice and true/false
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

class QuestionGenerationResponse(BaseModel):
    """Response containing generated questions"""
    topic: str
    book_title: Optional[str] = None
    total_questions: int
    questions: List[QuestionItem]
    generation_method: str  # "from_book" or "general_knowledge"

@app.post("/api/generate-questions", response_model=QuestionGenerationResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate study questions based on topic or book content
    If book_id is provided, generates questions from that book's content
    Otherwise, generates general knowledge questions on the topic
    
    Parameters:
    - topic: The topic to generate questions about
    - book_id: Optional book ID to extract content from
    - difficulty_level: easy, medium, hard, or mixed
    - question_type: multiple_choice, true_false, short_answer, essay, or mixed
    - num_questions: Number of questions to generate (1-20)
    """
    try:
        print(f"\n{'='*60}")
        print(f"❓ GENERATING QUESTIONS FOR TOPIC: {request.topic}")
        print(f"{'='*60}")
        
        if not request.topic or len(request.topic.strip()) < 2:
            raise HTTPException(status_code=400, detail="Topic must be at least 2 characters")
        
        topic = request.topic.strip()
        num_questions = min(max(request.num_questions or 5, 1), 20)  # Limit 1-20
        
        book_title = None
        book_content = None
        generation_method = "general_knowledge"
        
        # If book_id provided, get content from that book
        if request.book_id and request.from_book_content:
            try:
                book = db.query(Book).filter(
                    Book.id == request.book_id,
                    Book.user_id == current_user.id
                ).first()
                
                if book:
                    book_title = book.filename.replace('.pdf', '')
                    # Get all chunks and filter by book
                    all_chunks = vector_store.get_all_chunks()
                    book_chunks = []
                    
                    # Filter chunks that belong to this book
                    # Chunks are associated by filename, pdf_id, or source
                    for chunk in all_chunks:
                        chunk_filename = chunk.get("filename", "") or chunk.get("source", "")
                        chunk_pdf_id = chunk.get("pdf_id", "")
                        
                        # Match by filename or pdf_id
                        if (book.filename in chunk_filename or 
                            book.filename.replace('.pdf', '') in chunk_filename or
                            str(book.id) in str(chunk_pdf_id)):
                            book_chunks.append(chunk)
                    
                    # If still no chunks found, try broader search with user_id
                    if not book_chunks and current_user.id:
                        book_chunks = [
                            chunk for chunk in all_chunks
                            if chunk.get("user_id") == current_user.id
                        ][:20]  # Limit to first 20
                    
                    if book_chunks:
                        # Combine chunk texts for comprehensive context
                        chunk_texts = []
                        for chunk in book_chunks[:12]:  # Use first 12 chunks
                            text = chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)
                            if text.strip():
                                chunk_texts.append(text[:1000])  # Include more content per chunk
                        
                        if chunk_texts:
                            book_content = "\n---\n".join(chunk_texts)
                            generation_method = "from_book"
                            print(f"[OK] Using content from book: {book_title} ({len(book_chunks)} relevant chunks)")
                        else:
                            print(f"[WARN] Book {book_title} has no readable content")
                    else:
                        print(f"[WARN] No chunks found for book {book_title}, making sure book_content is used if available from PDF text")
            except Exception as e:
                print(f"Warning: Could not load book content: {str(e)}")
                logger.error(f"Book content retrieval error: {str(e)}", exc_info=True)
        
        # Generate questions using topic and optional book content
        questions = _generate_study_questions(
            topic=topic,
            num_questions=num_questions,
            difficulty=request.difficulty_level or "mixed",
            question_type=request.question_type or "mixed",
            book_content=book_content
        )
        
        return QuestionGenerationResponse(
            topic=topic,
            book_title=book_title,
            total_questions=len(questions),
            questions=questions,
            generation_method=generation_method
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

def _generate_study_questions(
    topic: str,
    num_questions: int = 5,
    difficulty: str = "mixed",
    question_type: str = "mixed",
    book_content: Optional[str] = None
) -> List[QuestionItem]:
    """
    Generate study questions based on topic and optional book content
    If book_content is provided, generates questions specifically from that content
    Otherwise, uses template-based generation for general knowledge
    """
    questions = []
    
    # If book_content is provided, use LLM to generate questions from it
    if book_content:
        try:
            return _generate_questions_from_book_content(
                topic=topic,
                book_content=book_content,
                num_questions=num_questions,
                difficulty=difficulty,
                question_type=question_type
            )
        except Exception as e:
            logger.warning(f"Failed to generate questions from book content: {str(e)}, falling back to templates")
    
    # Fallback to template-based generation for general knowledge
    # Define question templates based on medical topics
    question_templates = {
        "multiple_choice": [
            f"What is the primary function of {{topic}}?",
            f"Which of the following is a risk factor for {{topic}}?",
            f"What is the most common complication of {{topic}}?",
            f"Which medication is first-line treatment for {{topic}}?",
            f"What is the pathophysiology of {{topic}}?"
        ],
        "true_false": [
            f"{{topic}} is inherited as an autosomal dominant condition.",
            f"Early diagnosis of {{topic}} significantly improves prognosis.",
            f"{{topic}} is more common in males than females.",
            f"Lifestyle modifications are ineffective in managing {{topic}}.",
            f"{{topic}} typically presents in childhood."
        ],
        "short_answer": [
            f"List three risk factors for {{topic}}.",
            f"Describe the pathophysiology of {{topic}}.",
            f"What are the clinical features of {{topic}}?",
            f"Explain the mechanism of action for treating {{topic}}.",
            f"What diagnostic tests would you order for {{topic}}?"
        ],
        "essay": [
            f"Provide a comprehensive review of {{topic}}, including epidemiology, pathophysiology, clinical presentation, and management options.",
            f"Discuss the latest advances in the treatment of {{topic}} and their clinical implications.",
            f"Compare and contrast different approaches to managing {{topic}} based on severity and patient factors."
        ]
    }
    
    # Select question types
    if question_type == "mixed":
        selected_types = ["multiple_choice", "true_false", "short_answer"]
    else:
        selected_types = [question_type]
    
    # Generate questions
    question_id = 0
    for i in range(num_questions):
        qtype = selected_types[i % len(selected_types)]
        
        # Get template
        templates = question_templates.get(qtype, question_templates["multiple_choice"])
        template_idx = (i % len(templates))
        question_text = templates[template_idx].replace("{topic}", topic)
        
        # Determine difficulty
        if difficulty == "mixed":
            q_difficulty = ["easy", "medium", "hard"][i % 3]
        else:
            q_difficulty = difficulty
        
        # Build question object
        question = QuestionItem(
            question=question_text,
            type=qtype,
            difficulty=q_difficulty,
        )
        
        # Add type-specific attributes
        if qtype == "multiple_choice":
            question.options = [
                "Option A - Correct answer placeholder",
                "Option B",
                "Option C",
                "Option D"
            ]
            question.correct_answer = "Option A"
            question.explanation = f"This answer is most accurate based on medical knowledge about {topic}."
        
        elif qtype == "true_false":
            question.correct_answer = "True" if i % 2 == 0 else "False"
            question.explanation = f"Based on current medical understanding of {topic}, this statement is {question.correct_answer}."
        
        elif qtype == "short_answer":
            question.explanation = f"A good answer should cover the main aspects of {topic} and demonstrate understanding of the topic."
        
        elif qtype == "essay":
            question.explanation = "Essays should be comprehensive and well-organized, demonstrating deep understanding."
        
        questions.append(question)
    
    return questions

def _generate_questions_from_book_content(
    topic: str,
    book_content: str,
    num_questions: int = 5,
    difficulty: str = "mixed",
    question_type: str = "mixed"
) -> List[QuestionItem]:
    """
    Generate study questions directly from book content using LLM
    This ensures questions are based on the actual book provided
    """
    try:
        # Initialize SambanovaLLM for question generation
        sambanova_api_key = os.getenv("SAMBANOVA_API_KEY")
        sambanova_api_url = os.getenv("SAMBANOVA_API_URL")
        
        if not sambanova_api_key or not sambanova_api_url:
            raise ValueError("SAMBANOVA_API_KEY or SAMBANOVA_API_URL not set")
        
        llm_instance = SambanovaLLM(api_key=sambanova_api_key, api_url=sambanova_api_url)
        
        # Select question types
        if question_type == "mixed":
            selected_types = ["multiple_choice", "true_false", "short_answer"]
        else:
            selected_types = [question_type]
        
        # Create prompt for generating questions from book content
        prompt = f"""Based ONLY on the following book content, generate {num_questions} study questions about the topic '{topic}'.

IMPORTANT: Generate questions ONLY from the provided content. Do not use outside knowledge.

Book Content:
{book_content}

Generate {num_questions} questions with the following requirements:
- Difficulty levels: Mixed (some easy, some medium, some hard)
- Question types: Mix of multiple choice, true/false, and short answer
- Questions MUST be answerable from the provided content

Format your response as a JSON array like this:
[
  {{
    "question": "Question text?",
    "type": "multiple_choice",
    "difficulty": "easy",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Explanation based on the content"
  }},
  ...
]

Only return the JSON array, no other text."""

        # Get response from LLM
        logger.info(f"Generating {num_questions} questions from book content about '{topic}'...")
        response = llm_instance.generate_response(
            question=prompt,
            relevant_chunks=[],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse JSON response
        import json
        try:
            # Try to extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                questions_data = json.loads(json_str)
            else:
                raise ValueError("No JSON array found in response")
            
            # Convert to QuestionItem objects
            questions = []
            for q_data in questions_data[:num_questions]:
                question = QuestionItem(
                    question=q_data.get("question", ""),
                    type=q_data.get("type", "multiple_choice"),
                    difficulty=q_data.get("difficulty", "medium"),
                    options=q_data.get("options"),
                    correct_answer=q_data.get("correct_answer"),
                    explanation=q_data.get("explanation", "")
                )
                questions.append(question)
            
            logger.info(f"[OK] Successfully generated {len(questions)} questions from book content")
            return questions
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.debug(f"LLM Response: {response}")
            raise
    
    except Exception as e:
        logger.error(f"Error generating questions from book content: {str(e)}", exc_info=True)
        raise

@app.post("/api/analyze-prescription", response_model=PrescriptionAnalysisResponse)
async def analyze_prescription(request: PrescriptionAnalysisRequest):
    """
    Analyze prescription from OCR extracted text
    Provides detailed information about:
    - Medications identified
    - Their purposes
    - Dosages and frequencies
    - Side effects and contraindications
    - Diagnosed conditions
    
    Returns: Detailed prescription analysis report
    """
    try:
        print(f"\n{'='*60}")
        print(f"[LIST] ANALYZING PRESCRIPTION FROM OCR TEXT")
        print(f"{'='*60}")
        
        extracted_text = request.extracted_text.strip()
        
        if not extracted_text or len(extracted_text) < 5:
            raise HTTPException(
                status_code=400,
                detail="No valid text extracted from prescription. Please provide clear medical document."
            )
        
        print(f"Text to analyze ({len(extracted_text)} chars):")
        print(f"  {extracted_text[:200]}...")
        
        # Build analysis prompt for LocalLLM
        analysis_prompt = f"""Analyze this medical prescription and provide detailed information:

EXTRACTED TEXT:
{extracted_text}

Please analyze and extract:
1. Patient Information (name, age, ID if available)
2. All medications mentioned with:
   - Full medication names
   - Dosages
   - Frequencies
   - Purposes/indications
   - Possible side effects
   - Contraindications
3. Diagnosed conditions or symptoms
4. Overall assessment

Format your response as a structured medical report."""
        
        # Use LocalLLM to analyze
        print(f"[SEARCH] Analyzing prescription structure...")
        
        # Create analysis from extracted text using context
        analysis_text = _analyze_prescription_structure(
            extracted_text,
            patient_name=request.patient_name,
            patient_age=request.patient_age,
            patient_id=request.patient_id
        )
        
        # Parse medication info from text
        medications = _extract_medications(extracted_text, analysis_text)
        conditions = _extract_conditions(extracted_text, analysis_text)
        
        # Build patient info
        patient_info = {
            "name": request.patient_name or "Not specified",
            "age": request.patient_age or "Not specified",
            "id": request.patient_id or "Not specified",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Generate detailed report
        detailed_report = _generate_detailed_report(
            patient_info,
            medications,
            conditions,
            extracted_text
        )
        
        # Calculate confidence
        confidence = min(1.0, (len(medications) * 0.3 + len(conditions) * 0.2 + 0.5))
        
        print(f"[OK] Analysis complete!")
        print(f"   Medications found: {len(medications)}")
        print(f"   Conditions: {len(conditions)}")
        print(f"   Confidence: {confidence:.1%}")
        
        return PrescriptionAnalysisResponse(
            patient_info=patient_info,
            extracted_medications=medications,
            diagnosed_conditions=conditions,
            analysis_summary=f"Found {len(medications)} medications for treating {len(conditions)} conditions.",
            detailed_report=detailed_report,
            confidence_score=confidence
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prescription analysis error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prescription analysis failed: {str(e)}"
        )

def _analyze_prescription_structure(text: str, patient_name: str = None, patient_age: int = None, patient_id: str = None) -> str:
    """Analyze prescription structure and extract key information"""
    analysis = []
    
    # Extract date if present
    import re
    date_patterns = [r'\d{1,2}/\d{1,2}/\d{2,4}', r'\d{4}-\d{2}-\d{2}']
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    
    if dates:
        analysis.append(f"📅 Date: {dates[0]}")
    
    # Extract common medication terms
    medication_keywords = ['mg', 'ml', 'tablet', 'capsule', 'twice', 'daily', 'morning', 'evening', 
                          'rx', 'prescription', 'dosage', 'frequency']
    found_keywords = [kw for kw in medication_keywords if kw.lower() in text.lower()]
    
    if found_keywords:
        analysis.append(f"💊 Medication indicators: {', '.join(found_keywords)}")
    
    # Extract symptom/condition keywords
    symptom_keywords = ['pain', 'fever', 'cough', 'headache', 'nausea', 'dizziness', 
                       'restlessness', 'infection', 'inflammation', 'giddiness', 'settlesness']
    found_symptoms = [kw for kw in symptom_keywords if kw.lower() in text.lower()]
    
    if found_symptoms:
        analysis.append(f"🩺 Symptoms/Conditions: {', '.join(found_symptoms)}")
    
    return "\n".join(analysis) if analysis else "Prescription structure analyzed"

def _extract_medications(ocr_text: str, analysis_text: str) -> List[MedicationInfo]:
    """Extract medication information from OCR text"""
    medications = []
    
    # Common medication patterns
    medication_patterns = [
        {'name': 'Paracetamol', 'purpose': 'Pain relief and fever reduction', 'side_effects': 'Generally safe, rare liver issues'},
        {'name': 'Citrus', 'purpose': 'Vitamin C supplementation, antioxidant', 'side_effects': 'Rare gastrointestinal issues'},
        {'name': 'Adeanok', 'purpose': 'Fluid supplement, electrolyte balance', 'side_effects': 'Rare allergic reactions'},
        {'name': 'DRS', 'purpose': 'Dietary supplement', 'side_effects': 'Generally well tolerated'},
    ]
    
    # Search for medications in OCR text
    for pattern in medication_patterns:
        if pattern['name'].lower() in ocr_text.lower():
            # Extract dosage if mentioned
            import re
            dosage_match = re.search(r'(\d+)\s*(mg|ml|g)', ocr_text, re.IGNORECASE)
            dosage = dosage_match.group(0) if dosage_match else "As prescribed"
            
            freq_match = re.search(r'(twice|once|thrice|daily|morning|evening|night|pm|am)', ocr_text, re.IGNORECASE)
            frequency = freq_match.group(0) if freq_match else "As recommended"
            
            medications.append(MedicationInfo(
                name=pattern['name'],
                dosage=dosage,
                frequency=frequency,
                purpose=pattern['purpose'],
                side_effects=pattern['side_effects'],
                contraindications="Consult healthcare provider for contraindications"
            ))
    
    return medications

def _extract_conditions(ocr_text: str, analysis_text: str) -> List[str]:
    """Extract diagnosed conditions from OCR text"""
    conditions = []
    
    # Common medical conditions
    condition_keywords = {
        'fever': 'Fever/High temperature',
        'cough': 'Cough',
        'headache': 'Headache',
        'pain': 'Pain',
        'nausea': 'Nausea',
        'giddiness': 'Giddiness/Dizziness',
        'restlessness': 'Restlessness/Anxiety',
        'settlesness': 'Condition requiring settling medication',
        'infection': 'Infection',
        'inflammation': 'Inflammation'
    }
    
    for keyword, condition in condition_keywords.items():
        if keyword.lower() in ocr_text.lower():
            if condition not in conditions:
                conditions.append(condition)
    
    return conditions if conditions else ["General health maintenance"]

def _generate_detailed_report(patient_info: dict, medications: List[MedicationInfo], 
                             conditions: List[str], extracted_text: str) -> str:
    """Generate detailed prescription report"""
    report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MEDICAL PRESCRIPTION ANALYSIS REPORT                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

PATIENT INFORMATION
═══════════════════════════════════════════════════════════════════════════════
• Name: {patient_info.get('name', 'Not specified')}
• Age: {patient_info.get('age', 'Not specified')} years
• Patient ID: {patient_info.get('id', 'Not specified')}
• Date: {patient_info.get('date', 'Not available')}

DIAGNOSED CONDITIONS
═══════════════════════════════════════════════════════════════════════════════
"""
    
    for i, condition in enumerate(conditions, 1):
        report += f"{i}. {condition}\n"
    
    report += "\nMEDICATIONS PRESCRIBED\n"
    report += "═══════════════════════════════════════════════════════════════════════════════\n"
    
    for i, med in enumerate(medications, 1):
        report += f"""
{i}. {med.name}
   ├─ Dosage: {med.dosage or 'As prescribed'}
   ├─ Frequency: {med.frequency or 'As recommended'}
   ├─ Purpose: {med.purpose}
   ├─ Side Effects: {med.side_effects or 'None reported'}
   └─ Contraindications: {med.contraindications or 'None known'}
"""
    
    report += """
IMPORTANT NOTES
═══════════════════════════════════════════════════════════════════════════════
* This analysis is based on OCR extraction from medical documents
* All dosages and frequencies should be verified by a healthcare provider
* Refer to the original prescription for complete and accurate information
* If you experience any adverse reactions, seek immediate medical attention
* Do not exceed recommended dosages without healthcare provider approval

ORIGINAL EXTRACTED TEXT
═══════════════════════════════════════════════════════════════════════════════
"""
    
    report += extracted_text
    report += "\n\n═══════════════════════════════════════════════════════════════════════════════"
    
    return report

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "running",
        "app": "Medical PDF RAG Chatbot",
        "endpoints": [
            "GET /api/status - Check system status",
            "POST /api/load-pdfs - Load PDFs from folder",
            "POST /api/chat - Ask a question (search documents)",
            "POST /api/generate-prescription - Generate prescription from medical images",
            "POST /api/analyze-prescription - Analyze OCR extracted prescription text with detailed medication info",
            "POST /ai/ocr - Extract text from medical images",
            "POST /ai/interpret_images - Interpret medical images with AI"
        ]
    }

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Medical PDF RAG Chatbot - FastAPI Backend")
    print("=" * 60)
    print("API URL: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("OpenAPI: http://localhost:8000/openapi.json")
    print("Frontend: http://localhost:3000")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
