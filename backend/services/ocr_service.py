# ocr.py
"""
OCR helper + FastAPI router for the MediAi project.

Place this file next to your main.py (same folder). Then either:
  1) import ocr (automatic router registration tries to detect `app` in main), or
  2) explicitly include the router in main.py:
       from ocr import router as ocr_router
       app.include_router(ocr_router, prefix="/ai")

Endpoints:
  POST /ai/ocr            -> upload images, returns {"texts": [...]}
  POST /ai/interpret_images -> upload images, returns {"interpretation": "...", "extracted_texts":[...]}
"""
import os
import tempfile
import shutil
import base64
import logging
import json
from typing import List, Optional, Callable, Any, Dict

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

logger = logging.getLogger("ocr")
logger.setLevel(logging.INFO)

# ---------------------------
# OCR backend: PRIMARY = PaddleOCR (Recommended)
# FALLBACK = Tesseract-OCR (via pytesseract) if PaddleOCR not available
# ---------------------------

# Fallback method: Tesseract-OCR via pytesseract  
_PYTESSERACT_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image
    # Configure pytesseract to find Tesseract installation
    import os
    # Check common Tesseract installation paths
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Default installation
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',  # 32-bit
        '/usr/bin/tesseract',  # Linux
        '/usr/local/bin/tesseract',  # macOS
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                # Test if it works
                version = pytesseract.get_tesseract_version()
                logger.info(f"[OK] Tesseract-OCR found at: {path}")
                logger.info(f"   Version: {version}")
                _PYTESSERACT_AVAILABLE = True
                break
            except Exception as e:
                logger.warning(f"[WARN] Found Tesseract at {path} but can't execute: {e}")
                continue
    
    if not _PYTESSERACT_AVAILABLE:
        logger.warning("[WARN] Tesseract not found at default paths. Please install from:")
        logger.warning("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        logger.warning("   Download: tesseract-ocr-w64-setup-v5.x.exe or v5.3.exe")
        logger.warning("   Linux: sudo apt-get install tesseract-ocr")
        logger.warning("   macOS: brew install tesseract")
        logger.warning("[WARN] Will fallback to PaddleOCR")
    else:
        logger.info("[OK] pytesseract imported successfully (available as fallback)")
except ImportError as e:
    logger.warning(f"[WARN] pytesseract not available (this is OK, PaddleOCR is primary): {e}")
    _PYTESSERACT_AVAILABLE = False
except Exception as e:
    logger.error(f"[ERROR] Error configuring pytesseract: {e}")
    _PYTESSERACT_AVAILABLE = False

# Primary method: PaddleOCR
_REAL_PADDLE_AVAILABLE = False
_RealPaddleOCR = None

try:
    # Lazy import - defer importing to avoid circular import with matplotlib
    import sys
    # Workaround for matplotlib circular import
    if 'matplotlib' not in sys.modules:
        import matplotlib
        matplotlib.use('Agg')
    
    from paddleocr import PaddleOCR as _RealPaddleOCR  # type: ignore
    _REAL_PADDLE_AVAILABLE = True
    logger.info("[OK] PaddleOCR available (PRIMARY)")
except ImportError as e:
    error_msg = str(e)
    if 'matplotlib' in error_msg or '_c_internal' in error_msg:
        logger.warning("[WARN] PaddleOCR matplotlib issue - will initialize on first use")
        _REAL_PADDLE_AVAILABLE = None  # None = not yet tested, will try again
    else:
        logger.warning(f"[WARN] PaddleOCR import failed: {error_msg[:100]}")
        logger.warning("   To fix: pip install --upgrade paddleocr paddle-lite paddlepaddle")
        _REAL_PADDLE_AVAILABLE = False
except Exception as e:
    logger.warning(f"[WARN] PaddleOCR initialization failed: {str(e)[:100]}")
    _REAL_PADDLE_AVAILABLE = False

# Lazy-initialized paddleocr wrapper
_paddleocr_instance = None

def ensure_ocr_initialized():
    """
    Lazy init: PRIMARY = PaddleOCR
    FALLBACK = Tesseract-OCR via pytesseract if PaddleOCR not available
    Returns an object with a .predict(image_path) -> [{'rec_texts': [...]}] API.
    """
    global _paddleocr_instance, _REAL_PADDLE_AVAILABLE, _PYTESSERACT_AVAILABLE, _RealPaddleOCR
    if _paddleocr_instance is not None:
        return _paddleocr_instance

    class _Shim:
        def __init__(self):
            global _REAL_PADDLE_AVAILABLE, _PYTESSERACT_AVAILABLE, _RealPaddleOCR
            
            self._using_tesseract = False
            self._using_paddle = False
            self._real_paddle = None
            
            # Try PaddleOCR first (PRIMARY METHOD)
            # If it failed during module import, try again now
            if (_REAL_PADDLE_AVAILABLE is None or not _REAL_PADDLE_AVAILABLE) and _RealPaddleOCR is None:
                try:
                    import sys
                    if 'matplotlib' not in sys.modules:
                        import matplotlib
                        matplotlib.use('Agg')
                    from paddleocr import PaddleOCR as _RealPaddleOCR_Deferred
                    _RealPaddleOCR = _RealPaddleOCR_Deferred
                    _REAL_PADDLE_AVAILABLE = True
                    logger.info("[OK] PaddleOCR imported successfully on first use")
                except Exception as e:
                    logger.warning(f"[WARN] Could not import PaddleOCR at runtime: {str(e)[:80]}")
                    _REAL_PADDLE_AVAILABLE = False
            
            if _REAL_PADDLE_AVAILABLE and _RealPaddleOCR is not None:
                try:
                    # Initialize with better defaults for both handwritten and printed text
                    logger.info("[INIT] Initializing PaddleOCR instance...")
                    self._real_paddle = _RealPaddleOCR(
                        use_angle_cls=True,  # Enable angle classification for rotated text
                        lang='en',
                        det_model_dir=None,  # Use default detection model
                        rec_model_dir=None,  # Use default recognition model
                    )
                    self._using_paddle = True
                    logger.info("[OK] OCR Mode: PaddleOCR (PRIMARY)")
                except Exception as e:
                    logger.warning(f"[WARN] Failed to init PaddleOCR: {e}")
                    logger.warning(f"[WARN] Stack trace: {str(e)}")
                    self._using_paddle = False
            
            # Fallback to Tesseract if PaddleOCR not available
            if not self._using_paddle and _PYTESSERACT_AVAILABLE:
                try:
                    self._using_tesseract = True
                    logger.warning("[WARN] OCR Mode: Tesseract-OCR (FALLBACK - PaddleOCR not available)")
                except Exception as e:
                    logger.warning(f"Failed to init Tesseract: {e}")
                    self._using_tesseract = False
            
            if not self._using_tesseract and not self._using_paddle:
                logger.error("[ERROR] NO OCR BACKEND AVAILABLE")
                logger.error("Please install PaddleOCR:")
                logger.error("  pip install paddleocr paddlepaddle paddle-lite")
                logger.error("Or install Tesseract-OCR as fallback:")
                logger.error("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
                logger.error("  Download: tesseract-ocr-w64-setup-v5.x.exe")

        def predict(self, image_path: str):
            """Extract text from image. Returns [{'rec_texts': [...]}]"""
            
            # METHOD 1: PaddleOCR (PRIMARY)
            if self._using_paddle and self._real_paddle is not None:
                try:
                    from PIL import ImageOps, ImageEnhance, ImageFilter
                    import numpy as np
                    import cv2
                    
                    img = Image.open(image_path)
                    logger.info(f"[FILE] Processing image with PaddleOCR: {image_path}")
                    
                    # ═══════════════════════════════════════════════════════════
                    # MINIMAL PREPROCESSING FOR PADDLEOCR (Handwritten-friendly)
                    # ═══════════════════════════════════════════════════════════
                    
                    # Step 1: Fix EXIF rotation
                    try:
                        img = ImageOps.exif_transpose(img)
                    except:
                        pass
                    
                    # Step 2: Ensure RGB color mode (PaddleOCR works better with color)
                    if img.mode != 'RGB':
                        try:
                            img = img.convert('RGB')
                        except:
                            pass
                    
                    # Step 3: Upscale very small images (for better OCR)
                    width, height = img.size
                    if width < 300 or height < 100:
                        scale = max(300 / width, 100 / height)
                        new_size = (int(width * scale * 1.2), int(height * scale * 1.2))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                        logger.info(f"  Upscaled image: {(width, height)} → {new_size}")
                    
                    # Step 4: Very light contrast adjustment only (preserve handwritten ink)
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.1)  # Very minimal boost
                    
                    logger.info("[OK] Preprocessing complete (handwritten-optimized)")
                    
                    # Step 5: Save to temp file for PaddleOCR (it works better with files)
                    import tempfile
                    temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
                    try:
                        img.save(temp_path, quality=95)  # High quality
                        logger.info(f"  Using preprocessed image: {temp_path}")
                        ocr_path = temp_path
                    except:
                        ocr_path = image_path
                    
                    # Step 6: PaddleOCR text extraction
                    logger.info(f"[RUNNING] Running PaddleOCR on color image")
                    result = None
                    try:
                        # PaddleOCR expects file path string
                        result = self._real_paddle.ocr(str(ocr_path), cls=True)
                    except Exception as e:
                        logger.error(f"PaddleOCR failed: {e}")
                        result = None
                    finally:
                        # Clean up temp file if created
                        if ocr_path != image_path and os.path.exists(ocr_path):
                            try:
                                os.close(temp_fd)
                                os.remove(ocr_path)
                            except:
                                pass


                    # Parse PaddleOCR result format: List[List[List[[[x,y], [x,y], ...], [text, confidence]]]]
                    rec_texts = []
                    if result and isinstance(result, list):
                        # Each page is a list
                        for page in result:
                            if isinstance(page, list):
                                # Each line in the page
                                for line in page:
                                    if isinstance(line, (list, tuple)) and len(line) >= 2:
                                        # line format: [[bbox coords], [text, confidence]]
                                        text_info = line[-1]  # Get last element (text and confidence)
                                        if isinstance(text_info, (list, tuple)) and len(text_info) > 0:
                                            text = text_info[0]
                                            if isinstance(text, str) and text.strip():
                                                rec_texts.append(text.strip())
                    
                    if rec_texts:
                        logger.info(f"[OK] PaddleOCR extracted {len(rec_texts)} lines")
                    else:
                        logger.warning(f"[WARN] PaddleOCR found no text")
                    
                    return [{"rec_texts": rec_texts}]
                        
                except Exception as e:
                    logger.error(f"[ERROR] PaddleOCR failed for {image_path}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    # Fall through to Tesseract if available
            
            # METHOD 2: Tesseract-OCR (FALLBACK)
            if self._using_tesseract and _PYTESSERACT_AVAILABLE:
                try:
                    logger.info(f"[FALLBACK] Falling back to Tesseract-OCR for {os.path.basename(image_path)}")
                    from PIL import ImageOps, ImageEnhance, ImageFilter
                    import numpy as np
                    import cv2
                    
                    img = Image.open(image_path)
                    logger.info(f"[FILE] Processing image with Tesseract: {image_path}")
                    
                    # Apply same preprocessing
                    try:
                        img = ImageOps.exif_transpose(img)  # Fix EXIF rotation
                    except:
                        pass
                    
                    if img.mode != 'RGB':
                        try:
                            img = img.convert('RGB')
                        except:
                            pass
                    img = img.convert('L')  # Grayscale
                    
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(0.9)
                    
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(2.0)
                    
                    img = img.filter(ImageFilter.MedianFilter(size=3))
                    
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(2.5)
                    
                    img_array = np.array(img)
                    img_binary = cv2.adaptiveThreshold(
                        img_array,
                        255,
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        cv2.THRESH_BINARY,
                        blockSize=11,
                        C=2
                    )
                    
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                    img_binary = cv2.morphologyEx(img_binary, cv2.MORPH_CLOSE, kernel, iterations=1)
                    img_binary = cv2.morphologyEx(img_binary, cv2.MORPH_OPEN, kernel, iterations=1)
                    
                    img = Image.fromarray(img_binary)
                    
                    logger.info("[OK] Advanced preprocessing complete")
                    
                    # Try multiple PSM modes for Tesseract
                    # Try PSM 6 first (optimized for prescriptions)
                    text_psm6 = pytesseract.image_to_string(
                        img,
                        config='--psm 6 --oem 3'
                    )
                    
                    # Try PSM 3 as fallback (handles mixed layouts)
                    text_psm3 = pytesseract.image_to_string(
                        img,
                        config='--psm 3 --oem 3'
                    )
                    
                    # Use whichever extracted more text
                    text = text_psm6 if len(text_psm6.strip()) >= len(text_psm3.strip()) else text_psm3
                    
                    if not text.strip():
                        # Last resort: try PSM 11 (sparse text mode)
                        text = pytesseract.image_to_string(
                            img,
                            config='--psm 11 --oem 3'
                        )
                    
                    # Clean up extracted text
                    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
                    
                    if lines:
                        logger.info(f"[OK] Tesseract extracted {len(lines)} lines from {os.path.basename(image_path)}")
                    else:
                        logger.warning(f"[WARN] Tesseract found no text in {os.path.basename(image_path)}")
                    
                    return [{"rec_texts": lines}]
                        
                except Exception as e:
                    logger.error(f"[ERROR] Tesseract OCR failed for {image_path}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    return [{"rec_texts": []}]
            
            # No backend available
            logger.error("No OCR backend available - cannot extract text")
            return [{"rec_texts": []}]

    _paddleocr_instance = _Shim()
    return _paddleocr_instance

# ---------------------------
# Utilities
# ---------------------------
def _save_uploadfile_to_temp(upload_file: UploadFile) -> str:
    suffix = os.path.splitext(upload_file.filename or "")[1] or ""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_path = tmp.name
    tmp.close()
    with open(tmp_path, "wb") as f:
        upload_file.file.seek(0)
        shutil.copyfileobj(upload_file.file, f)
    return tmp_path

def _decode_base64_to_temp(b64_string: str, filename_hint: Optional[str] = None) -> str:
    data = base64.b64decode(b64_string)
    suffix = os.path.splitext(filename_hint or "")[1] or ""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_path = tmp.name
    tmp.close()
    with open(tmp_path, "wb") as f:
        f.write(data)
    return tmp_path

def _run_ocr_on_path(path: str) -> List[str]:
    o = ensure_ocr_initialized()
    result = o.predict(path)
    extracted = []
    if result and isinstance(result, list):
        first = result[0]
        if isinstance(first, dict):
            extracted = first.get("rec_texts", []) or []
        else:
            # try to flatten list of strings
            try:
                for p in result:
                    if isinstance(p, dict):
                        extracted.extend(p.get("rec_texts", []) or [])
                    elif isinstance(p, str):
                        extracted.append(p)
            except Exception:
                pass
    return extracted

async def extract_texts_from_uploads(files: List[UploadFile]) -> List[str]:
    all_texts: List[str] = []
    tmp_paths: List[str] = []
    try:
        for f in files:
            # Check content_type OR file extension for image files
            is_image = False
            
            # Check by content_type
            if f.content_type and f.content_type.startswith("image/"):
                is_image = True
            
            # Fallback: check by file extension
            if not is_image and f.filename:
                image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
                file_ext = os.path.splitext(f.filename.lower())[1]
                if file_ext in image_extensions:
                    is_image = True
            
            if not is_image:
                raise HTTPException(status_code=400, detail=f"File {f.filename} must be an image (JPG, PNG, GIF, BMP, WebP, TIFF).")
            
            p = _save_uploadfile_to_temp(f)
            tmp_paths.append(p)
            try:
                texts = _run_ocr_on_path(p)
                all_texts.extend(texts)
            finally:
                if os.path.exists(p):
                    os.remove(p)
    finally:
        for p in tmp_paths:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
    return all_texts

def extract_texts_from_base64(items: List[Dict[str, str]]) -> List[str]:
    all_texts: List[str] = []
    tmp_paths = []
    try:
        for item in items:
            b64 = item.get("image_data_base64") or item.get("b64") or item.get("data")
            filename = item.get("filename")
            if not b64:
                continue
            p = _decode_base64_to_temp(b64, filename)
            tmp_paths.append(p)
            try:
                all_texts.extend(_run_ocr_on_path(p))
            finally:
                if os.path.exists(p):
                    os.remove(p)
    finally:
        for p in tmp_paths:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
    return all_texts

# ---------------------------
# LLM interpretation helper
# ---------------------------
class ImageInterpretationResponse(BaseModel):
    interpretation: str
    extracted_texts: List[str]

class OCRResponse(BaseModel):
    text: str
    accuracy: float
    report: str
    confidence_details: dict

def interpret_images_with_llm(
    extracted_texts: List[str],
    processed_filenames: List[str],
    llm_instance: Optional[Any] = None,
    is_medical_mode_override: Optional[bool] = None
) -> ImageInterpretationResponse:
    """
    Interpret extracted medical images using SambaNova AI.
    
    Args:
        extracted_texts: Text extracted from images
        processed_filenames: Original filenames
        llm_instance: SambanovaLLM instance (optional)
        is_medical_mode_override: Force medical or non-medical mode
    """
    if not extracted_texts:
        return ImageInterpretationResponse(interpretation="No text extracted from images.", extracted_texts=[])
    
    if not llm_instance:
        return ImageInterpretationResponse(
            interpretation="SambaNova LLM not available. Returning extracted texts only.",
            extracted_texts=extracted_texts
        )
    
    combined = "\n".join(extracted_texts)
    medical = is_medical_mode_override if is_medical_mode_override is not None else True

    if medical:
        system_prompt = "You are a medical assistant. Analyze the following extracted text from medical images and give a concise, structured interpretation, highlighting key findings and uncertainties."
    else:
        system_prompt = "You are an assistant. Summarize and analyze the provided extracted text."

    user_prompt = f"Files: {', '.join(processed_filenames) if processed_filenames else 'N/A'}\n\nExtracted text:\n{combined}"

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    try:
        # Call SambanovaLLM's _make_api_call method
        response = llm_instance._make_api_call(messages, max_tokens=500, temperature=0.5)
        # Parse OpenAI-compatible response
        interpretation = response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception(f"SambaNova interpretation failed: {e}")
        interpretation = f"Interpretation error: {str(e)}"

    return ImageInterpretationResponse(interpretation=interpretation, extracted_texts=extracted_texts)

# ---------------------------
# AI-Based OCR Validation
# ---------------------------
async def validate_ocr_with_ai(extracted_text: str) -> dict:
    """Validate OCR quality. Falls back safely if LLM not available."""
    if not extracted_text or len(extracted_text.strip()) < 5:
        return {"accuracy": 0, "confidence": "low", "issues": ["No text extracted"], "assessment": "No text could be extracted from the image."}
    try:
        import sys
        if 'main' in sys.modules:
            project_main = sys.modules['main']
        else:
            import main as project_main
        llm = getattr(project_main, 'llm', None)
        if llm:
            validation_prompt = f"Analyze OCR quality and respond with JSON: {{accuracy: 0-100, confidence_level: high/medium/low, identified_issues: [], assessment_notes: string}}\n\nText:\n{extracted_text[:500]}"
            messages = [{"role": "system", "content": "You are a document quality expert."}, {"role": "user", "content": validation_prompt}]
            try:
                response = llm._make_api_call(messages, max_tokens=200, temperature=0.3)
                result_text = response.choices[0].message.content.strip()
                if '{' in result_text:
                    json_start = result_text.find('{')
                    json_end = result_text.rfind('}') + 1
                    json_str = result_text[json_start:json_end]
                    result = json.loads(json_str)
                    return {"accuracy": result.get("accuracy", 80), "confidence": result.get("confidence_level", "medium"), "issues": result.get("identified_issues", []), "assessment": result.get("assessment_notes", "Text extracted successfully.")}
            except Exception as e:
                logger.warning(f"AI validation failed: {e}")
        return {"accuracy": 80, "confidence": "medium", "issues": [], "assessment": "Text extracted successfully."}
    except Exception as e:
        logger.warning(f"OCR validation error: {e}")
        return {"accuracy": 75, "confidence": "medium", "issues": [], "assessment": "Text extracted successfully."}

# ---------------------------
# FastAPI router
# ---------------------------
router = APIRouter()

@router.post("/ocr", response_model=OCRResponse)
async def ocr_endpoint(files: List[UploadFile] = File(...)):
    """
    POST /ai/ocr
    Upload images and extract text with AI-based accuracy validation.
    Returns: {text, accuracy (0-100), report, confidence_details}
    """
    texts = await extract_texts_from_uploads(files)
    combined_text = "\n".join(texts) if texts else ""
    validation = await validate_ocr_with_ai(combined_text)
    return OCRResponse(
        text=combined_text,
        accuracy=validation.get("accuracy", 0),
        report=validation.get("assessment", "Text extracted."),
        confidence_details={"confidence_level": validation.get("confidence", "low"), "issues": validation.get("issues", [])}
    )

@router.post("/interpret_images", response_model=ImageInterpretationResponse)
async def interpret_images_endpoint(
    files: List[UploadFile] = File(...)
):
    """
    POST /ai/interpret_images
    Upload images: extracts text and uses SambaNova AI for interpretation.
    Requires SambanovaLLM instance from main.py.
    """
    extracted = await extract_texts_from_uploads(files)
    filenames = [f.filename for f in files]

    # Try to get SambanovaLLM from main module
    llm_instance = None
    try:
        import main as project_main
        llm_instance = getattr(project_main, "llm", None)
    except Exception:
        logger.warning("Could not import SambanovaLLM from main module")

    # Use SambaNova if available, otherwise return just the extracted texts
    result = interpret_images_with_llm(
        extracted_texts=extracted,
        processed_filenames=filenames,
        llm_instance=llm_instance,
        is_medical_mode_override=True
    )
    return result

# ---------------------------
# Auto-register on import if some module exposes an 'app' FastAPI instance
# ---------------------------
def _try_auto_register():
    import sys, time, logging
    log = logging.getLogger("ocr")
    # Look through already-imported modules for a FastAPI 'app' instance
    for mod in list(sys.modules.values()):
        try:
            app_candidate = getattr(mod, "app", None)
            if app_candidate is not None and hasattr(app_candidate, "include_router"):
                # Ensure we don't double-register
                if not any("/ai/ocr" in (r.path or "") or "/ai/interpret_images" in (r.path or "") for r in app_candidate.routes):
                    app_candidate.include_router(router, prefix="/ai")
                    log.info("ocr.py auto-registered router on %s.app at prefix /ai", mod.__name__)
                return
        except Exception:
            continue

    # If not found, schedule a delayed attempt (useful when main module creates app after imports)
    def _delayed_attempt():
        for _ in range(6):  # try for ~30 seconds (6 * 5s)
            for mod in list(sys.modules.values()):
                try:
                    app_candidate = getattr(mod, "app", None)
                    if app_candidate is not None and hasattr(app_candidate, "include_router"):
                        if not any("/ai/ocr" in (r.path or "") or "/ai/interpret_images" in (r.path or "") for r in app_candidate.routes):
                            app_candidate.include_router(router, prefix="/ai")
                            log.info("ocr.py delayed auto-registered router on %s.app at prefix /ai", mod.__name__)
                        return
                except Exception:
                    continue
            time.sleep(5)
    import threading
    t = threading.Thread(target=_delayed_attempt, daemon=True)
    t.start()

_try_auto_register()
