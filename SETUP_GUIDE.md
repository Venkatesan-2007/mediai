# Medical AI - Complete Setup Guide

## ✅ Backend - FIXED & WORKING

### Issues Fixed:
1. **PaddleOCR Model Check Blocking Startup** ✅
   - Was hanging during model connectivity check
   - Solution: Disabled with `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True`

2. **Wrong Database Connection** ✅
   - Was trying to connect to PostgreSQL instead of SQLite
   - Solution: Moved `load_dotenv()` to execute BEFORE service imports
   - Updated `.env` to use SQLite: `sqlite:///./database/medi_ai.db`

3. **PDF Upload Error** ✅
   - PDFLoader was not handling temp files correctly
   - Solution: Rewrote upload endpoint to use pdfplumber directly with better logging

4. **API Port Mismatch** ✅
   - Frontend was calling port 5000, backend on 8000
   - Solution: Updated all frontend API endpoints to port 8000

---

## 🚀 How to Start

### Option 1: Batch File (Windows)
```batch
g:\medi ai\start_backend.bat
```

### Option 2: PowerShell Script
```powershell
& "g:\medi ai\start_backend.ps1"
```

### Option 3: Manual
```bash
cd g:\medi ai\backend
set PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
python main.py
```

### Option 4: PowerShell (Recommended)
```powershell
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "True"
cd "g:\medi ai\backend"
python main.py
```

---

## ✅ API Endpoints

- **Status**: http://localhost:8000/api/status
- **API Docs**: http://localhost:8000/docs
- **Upload PDF**: POST /api/upload-pdf (requires auth)
- **Chat**: POST /api/chat (requires auth)
- **Uploaded PDFs**: GET /api/uploaded-pdfs (requires auth)

---

## 📝 Frontend Setup

Frontend is already configured to use `http://localhost:8000`

**Start Frontend:**
```bash
cd g:\medi ai\frontend\medi-ai
npm start
```

---

## 🔑 Environment Variables

File: `g:\medi ai\.env`

```ini
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Database (using SQLite for local development)
DATABASE_URL=sqlite:///./database/medi_ai.db

# JWT Secret
SECRET_KEY=your-secret-key-here-change-this-in-production

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

---

## 🧪 Testing

1. **Backend Status:**
   ```
   curl http://localhost:8000/api/status
   ```

2. **API Documentation:**
   ```
   Open http://localhost:8000/docs in browser
   ```

3. **Upload PDF:**
   - Go to Frontend: http://localhost:3000
   - Register/Login
   - Go to "My Books"
   - Upload a PDF

4. **Chat:**
   - Go to Chat page
   - Ask questions about your documents

---

## 🛠️ Troubleshooting

### Backend won't start
- Make sure Ollama is running: `ollama serve`
- Check `.env` file exists with correct DB path
- Try: `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True python main.py`

### PDF upload fails
- Check backend logs for detailed error
- Make sure PDF is valid and not corrupted
- Check PDF has readable text (not just images)

### No PDFs in chat
- Upload PDFs first in "My Books" section
- Check backend logs: `vector_store added X chunks`
- Verify database connection is working

### API Port Already in Use
If port 8000 is busy:
1. Find the process: `netstat -ano | findstr :8000`
2. Kill it: `taskkill /PID <PID> /F`
3. Or change port in `main.py`: line ~1700

---

## 📊 File Structure

```
g:\medi ai\
├── backend/
│   ├── main.py (FastAPI app)
│   ├── requirements.txt
│   ├── database/
│   │   ├── medi_ai.db (SQLite)
│   │   └── chroma_db/
│   └── services/
│       ├── vector_store.py (FAISS)
│       ├── simple_embeddings.py (TF-IDF)
│       ├── ollama_service.py
│       ├── database.py
│       └── ...
├── frontend/
│   └── medi-ai/ (React app)
│       ├── package.json
│       ├── .env
│       └── src/
├── .env (main config)
├── start_backend.bat
└── start_backend.ps1
```

---

## ✅ Verified Working
- ✓ Backend starts without hanging
- ✓ API responds to requests
- ✓ SQLite database works
- ✓ Ollama integration ready
- ✓ PDF upload endpoint fixed
- ✓ Embeddings service initialized
- ✓ Frontend connecting to correct port

---

## 🎯 Next Steps

1. **Start Backend**: Run one of the startup commands above
2. **Start Frontend**: `npm start` from `frontend/medi-ai`
3. **Register**: Create account at http://localhost:3000
4. **Upload PDF**: Upload medical documents in "My Books"
5. **Chat**: Ask questions about your documents

---

**Everything is ready to use! 🎉**
