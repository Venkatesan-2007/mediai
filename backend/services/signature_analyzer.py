"""
Signature & Prescription Analysis Service
Uses PaddleOCR (via centralized ocr_service) for text extraction and Ollama for AI-based analysis
"""
import logging
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Dict, List, Tuple
import io
import os
from .ocr_service import ensure_ocr_initialized

logger = logging.getLogger(__name__)


class SignatureAnalyzer:
    """
    Analyzes prescription signatures and handwritten content using PaddleOCR
    Provides medical analysis via Ollama LLM
    """
    
    def __init__(self, llm=None):
        """
        Initialize signature analyzer
        
        Args:
            llm: Ollama LLM service instance (optional for analysis)
        """
        self.llm = llm
        self.ocr = ensure_ocr_initialized()
        logger.info("[OK] SignatureAnalyzer initialized with PaddleOCR")
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy with PaddleOCR
        - Fix rotations
        - Enhance contrast minimally
        - Denoise if needed
        
        Note: PaddleOCR handles preprocessing internally, but additional preprocessing 
        can help with very poor quality images
        """
        try:
            # Convert PIL Image to numpy array
            img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 1. Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            
            # 2. Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            
            # 3. Apply thresholding (binary)
            _, thresh = cv2.threshold(denoised, 127, 255, cv2.THRESH_OTSU)
            
            # 4. Dilate to connect broken lines
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            dilated = cv2.dilate(thresh, kernel, iterations=1)
            
            # Convert back to PIL Image
            processed = Image.fromarray(dilated)
            return processed
            
        except Exception as e:
            logger.error(f"Error during image preprocessing: {e}")
            return image  # Return original if processing fails
    
    def extract_text_with_paddle(self, image: Image.Image, image_path: Optional[str] = None) -> Dict:
        """
        Extract text from image using PaddleOCR
        
        Args:
            image: PIL Image object
            image_path: Optional file path for OCR processing
        
        Returns:
            {
                'success': bool,
                'text': extracted text,
                'confidence': average confidence score (0-100),
                'details': per-word confidences
            }
        """
        try:
            logger.info("Extracting text with PaddleOCR...")
            
            # Save image to temp file if needed (PaddleOCR works better with file paths)
            if not image_path:
                import tempfile
                temp_fd, image_path = tempfile.mkstemp(suffix='.png')
                try:
                    image.save(image_path, 'PNG')
                finally:
                    os.close(temp_fd)
                cleanup_temp = True
            else:
                cleanup_temp = False
            
            try:
                # Use PaddleOCR for extraction
                result = self.ocr.predict(image_path)
                
                # Parse PaddleOCR result format: List[List[[[x,y], [x,y], ...], [text, confidence]]]]
                extracted_text_parts = []
                confidences_list = []
                word_details = []
                
                if result and isinstance(result, list):
                    for page in result:
                        if isinstance(page, list):
                            for line in page:
                                if isinstance(line, (list, tuple)) and len(line) >= 2:
                                    text_info = line[-1]
                                    if isinstance(text_info, (list, tuple)) and len(text_info) > 0:
                                        text = text_info[0]
                                        conf = text_info[1] if len(text_info) > 1 else 0.8
                                        
                                        if isinstance(text, str) and text.strip():
                                            extracted_text_parts.append(text.strip())
                                            confidence_percent = round(conf * 100, 1) if isinstance(conf, float) else 80
                                            confidences_list.append(confidence_percent)
                                            word_details.append({
                                                'word': text.strip(),
                                                'confidence': confidence_percent
                                            })
                
                extracted_text = ' '.join(extracted_text_parts)
                avg_confidence = sum(confidences_list) / len(confidences_list) if confidences_list else 0
                
                logger.info(f"Extracted {len(word_details)} words with {avg_confidence:.1f}% avg confidence")
                
                return {
                    'success': True,
                    'text': extracted_text.strip(),
                    'confidence': round(avg_confidence, 1),
                    'word_count': len(word_details),
                    'details': word_details[:20]  # Top 20 words for detail
                }
            finally:
                # Cleanup temp file if created
                if cleanup_temp and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"PaddleOCR extraction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0
            }
    
    # Alias for backward compatibility
    def extract_text_with_tesseract(self, image: Image.Image) -> Dict:
        """Backward compatibility wrapper - uses PaddleOCR now"""
        return self.extract_text_with_paddle(image)
    
    def analyze_prescription_with_ollama(
        self,
        extracted_text: str,
        patient_info: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze extracted prescription text using Ollama LLM
        
        Args:
            extracted_text: Text extracted from prescription
            patient_info: Optional patient information {name, age, id}
        
        Returns:
            {
                'analysis': AI-generated analysis,
                'medications': extracted medications list,
                'warnings': any warnings or concerns
            }
        """
        if not self.llm:
            logger.warning("LLM not available for prescription analysis")
            return {
                'success': False,
                'error': 'LLM service not initialized',
                'analysis': 'Please ensure Ollama is running'
            }
        
        try:
            # Build analysis prompt
            patient_context = ""
            if patient_info:
                if patient_info.get('name'):
                    patient_context += f"Patient Name: {patient_info['name']}\n"
                if patient_info.get('age'):
                    patient_context += f"Patient Age: {patient_info['age']}\n"
                if patient_info.get('id'):
                    patient_context += f"Patient ID: {patient_info['id']}\n"
            
            prompt = f"""You are a medical assistant reviewing an OCR-extracted prescription.

{patient_context}

EXTRACTED PRESCRIPTION TEXT:
{extracted_text}

Please provide:
1. **Medications Identified**: List each medication, dosage, and frequency
2. **Potential Issues**: Any unclear instructions, dosage concerns, or drug interactions
3. **Summary**: Brief medical summary suitable for patient review

Be concise and focus on safety and clarity."""
            
            logger.info("Analyzing prescription with Ollama...")
            
            # Generate analysis
            analysis = self.llm.generate_response(
                question="",
                relevant_chunks=[prompt],
                max_tokens=512,
                temperature=0.3
            )
            
            # Parse medications from the response
            medications = self._extract_medications(analysis)
            
            return {
                'success': True,
                'analysis': analysis,
                'medications': medications,
                'warnings': self._identify_warnings(analysis)
            }
            
        except Exception as e:
            logger.error(f"Ollama prescription analysis error: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': 'Could not generate AI analysis'
            }
    
    def _extract_medications(self, analysis_text: str) -> List[str]:
        """Extract medication names from analysis"""
        # Simple extraction - looks for common medication patterns
        import re
        
        medications = []
        
        # Pattern matches: "medication_name dosage frequency"
        # This is a simplified pattern - can be enhanced
        phrase_list = [
            r'(\w+\s+\w+s?)\s+(\d+\s*(?:mg|ml|g|units?)?)',
            r'**Medications?:**\s*([\w\s,]+)',
        ]
        
        for pattern in phrase_list:
            matches = re.findall(pattern, analysis_text, re.IGNORECASE)
            medications.extend([m[0] if isinstance(m, tuple) else m for m in matches])
        
        return list(set(medications))[:10]  # Return unique, limit to 10
    
    def _identify_warnings(self, analysis_text: str) -> List[str]:
        """Identify potential warnings in analysis"""
        warnings = []
        
        warning_keywords = [
            'interaction',
            'contraindication',
            'allergy',
            'caution',
            'warning',
            'severe',
            'critical',
            'unclear',
            'incomplete',
            'dosage concern'
        ]
        
        analysis_lower = analysis_text.lower()
        
        for keyword in warning_keywords:
            if keyword in analysis_lower:
                # Extract sentence containing warning
                sentences = analysis_text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        warnings.append(sentence.strip())
                        break
        
        return warnings[:5]  # Return top 5 warnings
    
    def analyze_signature_image(
        self,
        image: Image.Image,
        patient_info: Optional[Dict] = None
    ) -> Dict:
        """
        Complete signature/prescription analysis pipeline
        
        Args:
            image: PIL Image object
            patient_info: Optional patient information
        
        Returns:
            Complete analysis result dictionary
        """
        logger.info("Starting signature analysis pipeline...")
        
        # Step 1: OCR extraction
        ocr_result = self.extract_text_with_tesseract(image)
        
        if not ocr_result['success']:
            return {
                'success': False,
                'error': ocr_result.get('error', 'OCR extraction failed'),
                'extracted_text': '',
                'analysis': None,
                'ocr_confidence': 0
            }
        
        extracted_text = ocr_result['text']
        confidence = ocr_result['confidence']
        
        # Step 2: AI Analysis
        analysis_result = self.analyze_prescription_with_ollama(
            extracted_text,
            patient_info
        )
        
        # Combined result
        return {
            'success': True,
            'extracted_text': extracted_text,
            'ocr_confidence': confidence,
            'ocr_word_count': ocr_result['word_count'],
            'ocr_details': ocr_result['details'],
            'analysis': analysis_result.get('analysis', ''),
            'medications': analysis_result.get('medications', []),
            'warnings': analysis_result.get('warnings', []),
            'ai_analysis_available': analysis_result.get('success', False)
        }
