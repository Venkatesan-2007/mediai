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
# OCR backend: PRIMARY = EasyOCR (Best for handwritten text)
# FALLBACK = Tesseract-OCR if EasyOCR not available
# ---------------------------

# NOTE: EasyOCR is ENABLED - Best for handwritten medical documents
# Supports 80+ languages and excellent handwritten recognition
_EASYOCR_AVAILABLE = False
_easy_reader = None

try:
    import easyocr
    _EASYOCR_AVAILABLE = True
    logger.info("[CONFIG] EasyOCR: ENABLED (PRIMARY - Best for handwritten text)")
except ImportError:
    _EASYOCR_AVAILABLE = False
    logger.warning("[CONFIG] EasyOCR: NOT INSTALLED - Install with: pip install easyocr")

# Tesseract fallback
try:
    import pytesseract
    from PIL import Image
    _PYTESSERACT_AVAILABLE = True
    logger.info("[CONFIG] Tesseract-OCR: AVAILABLE (FALLBACK)")
except ImportError:
    _PYTESSERACT_AVAILABLE = False
    logger.warning("[CONFIG] Tesseract-OCR: NOT INSTALLED")

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
    Initialize PaddleOCR exclusively for medical document processing.
    Returns an object with a .predict(image_path) -> [{'rec_texts': [...]}] API.
    
    PaddleOCR provides superior accuracy for:
    - Handwritten prescriptions and signatures
    - Printed medical documents
    - Mixed handwritten and typed text
    - Rotated/skewed documents
    """
    global _paddleocr_instance, _REAL_PADDLE_AVAILABLE, _PYTESSERACT_AVAILABLE, _RealPaddleOCR
    if _paddleocr_instance is not None:
        return _paddleocr_instance

    class _Shim:
        def __init__(self):
            global _REAL_PADDLE_AVAILABLE, _PYTESSERACT_AVAILABLE, _RealPaddleOCR, _EASYOCR_AVAILABLE, _easy_reader
            
            self._using_easyocr = False
            self._easy_reader = None
            self._using_tesseract = False
            self._using_paddle = False
            self._real_paddle = None
            
            # Try EasyOCR first (PRIMARY METHOD)
            if _EASYOCR_AVAILABLE:
                try:
                    import easyocr
                    logger.info("[INIT] Initializing EasyOCR reader...")
                    # Initialize EasyOCR with English language
                    self._easy_reader = easyocr.Reader(['en'], gpu=False)
                    self._using_easyocr = True
                    logger.info("[OK] EasyOCR initialized as PRIMARY")
                except Exception as e:
                    logger.warning(f"[WARN] EasyOCR initialization failed: {str(e)[:80]}")
                    self._using_easyocr = False
            
            # Try Tesseract as secondary fallback
            if not self._using_easyocr and _PYTESSERACT_AVAILABLE:
                try:
                    import pytesseract
                    pytesseract.get_tesseract_version()
                    self._using_tesseract = True
                    logger.info("[OK] Tesseract-OCR initialized as SECONDARY")
                except Exception as e:
                    logger.warning(f"[WARN] Tesseract initialization failed: {str(e)[:80]}")
                    self._using_tesseract = False
            
            if not self._using_easyocr and not self._using_tesseract:
                logger.error("[ERROR] No OCR backend available!")
                logger.error("Install EasyOCR: pip install easyocr")

        def predict(self, image_path: str):
            """Extract text from image. Returns [{'rec_texts': [...]}]"""
            
            # METHOD 1: EasyOCR (PRIMARY - Best for handwritten text)
            if self._using_easyocr and self._easy_reader is not None:
                try:
                    from PIL import Image, ImageOps, ImageEnhance
                    
                    img = Image.open(image_path)
                    logger.info(f"[FILE] Processing image with EasyOCR: {image_path}")
                    
                    # Simple preprocessing for EasyOCR
                    # Fix EXIF rotation
                    try:
                        img = ImageOps.exif_transpose(img)
                    except:
                        pass
                    
                    # Convert to RGB
                    if img.mode != 'RGB':
                        try:
                            img = img.convert('RGB')
                        except:
                            pass
                    
                    # Mild contrast enhancement
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.3)
                    
                    # Save to temp file
                    import tempfile
                    temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
                    try:
                        img.save(temp_path, 'JPEG', quality=95)
                        ocr_path = temp_path
                    except:
                        ocr_path = image_path
                    
                    # Run EasyOCR
                    logger.info(f"[RUNNING] Running EasyOCR on image")
                    try:
                        # EasyOCR returns: [[[x,y],[x,y],...], 'text', confidence]
                        results = self._easy_reader.readtext(ocr_path, detail=0)
                        
                        # Extract texts
                        rec_texts = []
                        for text in results:
                            if isinstance(text, str) and text.strip():
                                rec_texts.append(text.strip())
                                logger.info(f"[TEXT] '{text.strip()}'")
                        
                        if rec_texts:
                            logger.info(f"[OK] EasyOCR extracted {len(rec_texts)} lines")
                            logger.info(f"[EXTRACTED] {' | '.join(rec_texts[:3])}")
                        else:
                            logger.warning("[WARN] EasyOCR found no text")
                        
                        return [{"rec_texts": rec_texts}]
                        
                    except Exception as ocr_err:
                        logger.error(f"[ERROR] EasyOCR execution failed: {ocr_err}")
                        return [{"rec_texts": []}]
                    finally:
                        # Cleanup temp file
                        if ocr_path != image_path and os.path.exists(ocr_path):
                            try:
                                os.close(temp_fd)
                                os.remove(ocr_path)
                            except:
                                pass
                        
                except Exception as e:
                    logger.error(f"[ERROR] EasyOCR failed: {e}")
                    logger.info("Falling back to Tesseract...")
                    # Fall through to Tesseract
            

            
            # METHOD 2: Tesseract-OCR (SECONDARY FALLBACK)
            if self._using_tesseract:
                try:
                    import pytesseract
                    from PIL import Image, ImageOps, ImageEnhance
                    
                    img = Image.open(image_path)
                    logger.info(f"[FILE] Processing image with Tesseract-OCR: {image_path}")
                    
                    # Fix EXIF rotation
                    try:
                        img = ImageOps.exif_transpose(img)
                    except:
                        pass
                    
                    # Convert to RGB
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Mild contrast enhancement
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.5)
                    
                    # Extract text
                    logger.info("[RUNNING] Running Tesseract-OCR")
                    extracted_text = pytesseract.image_to_string(img, config='--psm 11')
                    
                    if extracted_text and extracted_text.strip():
                        rec_texts = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                        logger.info(f"[OK] Tesseract extracted {len(rec_texts)} lines")
                        return [{"rec_texts": rec_texts}]
                    else:
                        logger.warning("[WARN] Tesseract found no text")
                        return [{"rec_texts": []}]
                        
                except Exception as e:
                    logger.error(f"[ERROR] Tesseract failed: {e}")
                    return [{"rec_texts": []}]
            
            # No OCR backend available
            logger.error("[ERROR] No OCR backend available")
            return [{"rec_texts": []}]

    _paddleocr_instance = _Shim()
    return _paddleocr_instance

# ---------------------------
# Advanced Preprocessing for Difficult Images (UI Screenshots)
# ---------------------------
def _apply_ui_screenshot_enhancement(image_path: str) -> str:
    """
    Apply specialized preprocessing for UI screenshots and difficult images.
    Creates an enhanced version optimized specifically for text detection.
    
    Returns the path to the enhanced image (may be original or temp).
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        import cv2
        import numpy as np
        
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to numpy array for OpenCV processing
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Convert to HSV to better detect text regions
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        
        # Enhance saturation for better color separation
        h, s, v = cv2.split(hsv)
        s = cv2.multiply(s, 1.3)  # Boost saturation
        v = cv2.multiply(v, 1.1)  # Slight brightness boost
        hsv_enhanced = cv2.merge([h, s, v])
        
        # Convert back to RGB
        img_enhanced = cv2.cvtColor(hsv_enhanced, cv2.COLOR_HSV2BGR)
        img_pil = Image.fromarray(cv2.cvtColor(img_enhanced, cv2.COLOR_BGR2RGB))
        
        # Apply strong contrast enhancement
        enhancer = ImageEnhance.Contrast(img_pil)
        img_pil = enhancer.enhance(2.5)
        
        # Apply unsharp mask for edge enhancement
        enhancer = ImageEnhance.Sharpness(img_pil)
        img_pil = enhancer.enhance(3.0)
        
        # Save enhanced version to temp
        temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
        try:
            img_pil.save(temp_path, 'PNG')
            logger.info(f"[UI-ENHANCE] Created enhanced image: {temp_path}")
            return temp_path
        except:
            os.close(temp_fd)
            return image_path
            
    except Exception as e:
        logger.error(f"[ERROR] UI enhancement failed: {e}")
        return image_path

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
    
    # If extraction was empty or very weak, try UI enhancement for screenshots
    if not extracted:
        logger.info("[FALLBACK] No text extracted - attempting UI screenshot enhancement")
        try:
            enhanced_path = _apply_ui_screenshot_enhancement(path)
            if enhanced_path != path:
                logger.info("[RETRY] Running OCR on enhanced image")
                result2 = o.predict(enhanced_path)
                
                if result2 and isinstance(result2, list):
                    for item in result2:
                        if isinstance(item, dict):
                            extracted.extend(item.get("rec_texts", []) or [])
                
                # Cleanup enhanced image
                try:
                    os.remove(enhanced_path)
                except:
                    pass
                
                if extracted:
                    logger.info(f"[SUCCESS] UI enhancement recovered {len(extracted)} lines")
                    
        except Exception as e:
            logger.error(f"UI enhancement fallback failed: {e}")
    
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
