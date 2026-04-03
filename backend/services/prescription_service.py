"""
Prescription Generation Service
Generates medical prescriptions from clinical findings using AI
"""
import json
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

logger = logging.getLogger("prescription_service")
logger.setLevel(logging.INFO)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PrescriptionMedicine(BaseModel):
    """Individual medicine in prescription"""
    medicine: str
    dosage: str
    unit: str  # e.g., mg, ml, tablet
    frequency: str  # e.g., twice daily, every 8 hours
    duration: str  # e.g., 7 days, 2 weeks
    notes: Optional[str] = None


class StructuredPrescription(BaseModel):
    """Structured prescription with medicines list"""
    medicines: List[PrescriptionMedicine]
    diagnosis: Optional[str] = None
    patient_notes: Optional[str] = None
    doctor_notes: Optional[str] = None


class PrescriptionResponse(BaseModel):
    """Complete prescription response with structured + narrative format"""
    structured: StructuredPrescription
    narrative: str
    extracted_text: str
    generation_method: str = "SambaNova AI"


# ============================================================================
# PRESCRIPTION GENERATION SERVICE
# ============================================================================

class PrescriptionGenerationService:
    """Service for generating prescriptions from clinical findings"""
    
    def __init__(self, sambanova_llm):
        """
        Initialize with SambaNova LLM client
        
        Args:
            sambanova_llm: Initialized SambanovaLLM instance
        """
        self.llm = sambanova_llm
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response which may contain additional text
        
        Args:
            response_text: Raw response from LLM
        
        Returns: Parsed JSON dict
        """
        try:
            # Try direct JSON parse first
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON block in response
        try:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        logger.warning("Could not parse JSON from LLM response, returning empty prescription")
        return {
            "prescription": [],
            "narrative": f"Generated narrative: {response_text[:500]}..."
        }
    
    def generate_prescription(
        self,
        clinical_text: str,
        patient_info: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.5
    ) -> PrescriptionResponse:
        """
        Generate prescription from clinical findings using SambaNova AI
        
        Args:
            clinical_text: Extracted clinical findings from medical image/document
            patient_info: Optional patient information context
            max_tokens: Maximum response tokens
            temperature: Model temperature (0.0-1.0)
        
        Returns: PrescriptionResponse with structured + narrative format
        """
        
        if not clinical_text or not clinical_text.strip():
            return PrescriptionResponse(
                structured=StructuredPrescription(
                    medicines=[],
                    diagnosis="No clinical data provided",
                    doctor_notes="Unable to generate prescription without clinical information"
                ),
                narrative="No clinical findings were extracted from the provided image.",
                extracted_text="",
                generation_method="Error"
            )
        
        # Build the prescription generation prompt
        patient_context = f"\nPatient Information: {patient_info}" if patient_info else ""
        
        system_prompt = """You are an expert medical AI assistant specializing in prescription generation.

Your task is to analyze clinical findings and generate appropriate prescriptions.

IMPORTANT: Always respond with a valid JSON object in this exact format:
{
  "prescription": [
    {
      "medicine": "medicine name",
      "dosage": "numeric value",
      "unit": "mg/ml/tablet/etc",
      "frequency": "dosage frequency",
      "duration": "treatment duration",
      "notes": "any special notes"
    }
  ],
  "diagnosis": "identified diagnosis",
  "narrative": "detailed medical report with findings and recommendations"
}

Rules:
1. Always respond with valid JSON only
2. If uncertain about any medication, include a note in the JSON
3. Include warnings or contraindications in notes field
4. Generate realistic, evidence-based prescriptions
5. Consider standard dosing guidelines for medications
"""

        user_prompt = f"""Based on the following clinical findings, generate an appropriate prescription in JSON format:

{clinical_text}{patient_context}

Please analyze the clinical findings and provide:
1. A structured prescription with medicines (dosage, frequency, duration)
2. Identified diagnosis
3. A narrative medical report summarizing findings and recommendations

Respond ONLY with the JSON object, no additional text."""

        try:
            logger.info("📋 Calling SambaNova API for prescription generation...")
            
            # Call SambaNova API
            response = self.llm._make_api_call(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract response text
            if response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content.strip()
                logger.info("[OK] Prescription generated successfully")
            else:
                raise Exception("Invalid response format from SambaNova API")
            
            # Parse JSON response
            prescription_data = self._extract_json_from_response(response_text)
            
            # Build structured prescription
            medicines = []
            if prescription_data.get("prescription"):
                for med in prescription_data["prescription"]:
                    try:
                        medicines.append(PrescriptionMedicine(
                            medicine=med.get("medicine", ""),
                            dosage=str(med.get("dosage", "")),
                            unit=med.get("unit", ""),
                            frequency=med.get("frequency", ""),
                            duration=med.get("duration", ""),
                            notes=med.get("notes")
                        ))
                    except Exception as e:
                        logger.warning(f"Could not parse medicine entry: {e}")
            
            structured = StructuredPrescription(
                medicines=medicines,
                diagnosis=prescription_data.get("diagnosis"),
                doctor_notes=prescription_data.get("doctor_notes"),
                patient_notes=prescription_data.get("patient_notes")
            )
            
            return PrescriptionResponse(
                structured=structured,
                narrative=prescription_data.get("narrative", response_text),
                extracted_text=clinical_text,
                generation_method="SambaNova AI (ALLaM-7B)"
            )
        
        except Exception as e:
            logger.error(f"[ERROR] Prescription generation failed: {str(e)}")
            
            # Return error response
            return PrescriptionResponse(
                structured=StructuredPrescription(
                    medicines=[],
                    diagnosis="Generation Error",
                    doctor_notes=str(e)
                ),
                narrative=f"Error generating prescription: {str(e)}",
                extracted_text=clinical_text,
                generation_method="Error"
            )
