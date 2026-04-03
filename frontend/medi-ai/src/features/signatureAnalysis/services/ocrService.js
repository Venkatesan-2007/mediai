/**
 * OCR Service - Backend API Implementation
 * Handles image text extraction for prescription/signature analysis
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Extract text from an image file
 * @param {File} imageFile - The image file to process
 * @param {function} progressCallback - Optional callback for progress updates
 * @returns {Promise} Promise with extracted text
 */
export const extractTextFromImage = (imageFile, progressCallback) => {
    return new Promise((resolve, reject) => {
        // Validate file
        if (!imageFile) {
            reject({ success: false, message: 'No image file provided' });
            return;
        }

        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'];
        if (!validTypes.includes(imageFile.type)) {
            reject({ success: false, message: 'Invalid file type. Please upload a JPG, PNG, or GIF image.' });
            return;
        }

        // Validate file size (max 10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (imageFile.size > maxSize) {
            reject({ success: false, message: 'File too large. Maximum size is 10MB.' });
            return;
        }

        // Create FormData to send image to backend
        const formData = new FormData();
        formData.append('files', imageFile);

        // Report progress
        if (progressCallback) {
            progressCallback(30);
        }

        // Call backend OCR endpoint
        // Note: Tesseract-OCR can take time, especially for:
        // - First initialization (loads language models)
        // - Handwritten text (harder to process)
        // - Large/complex images
        // Timeout increased to 180 seconds (3 minutes) to allow full processing
        axios.post(`${API_URL}/ai/ocr`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            timeout: 180000  // 180 seconds (3 minutes) for Tesseract + fallback processing
        })
            .then((response) => {
                if (progressCallback) {
                    progressCallback(100);
                }

                const data = response.data;
                
                // Handle new AI-validated format: {text, accuracy, report, confidence_details}
                if (data.text !== undefined && data.accuracy !== undefined) {
                    const extractedText = data.text.trim();
                    if (extractedText.length > 0) {
                        resolve({
                            success: true,
                            text: extractedText,
                            accuracy: Math.round(data.accuracy),
                            report: data.report,
                            confidence_details: data.confidence_details || {}
                        });
                    } else {
                        reject({
                            success: false,
                            message: 'No text could be extracted from the image. Please try a clearer image.'
                        });
                    }
                } 
                // Fallback: Handle legacy format {texts: [...]}
                else if (data.texts && Array.isArray(data.texts) && data.texts.length > 0) {
                    const extractedText = data.texts.join('\n').trim();
                    if (extractedText.length > 0) {
                        resolve({
                            success: true,
                            text: extractedText,
                            accuracy: 75,
                            report: 'Text extracted'
                        });
                    } else {
                        reject({
                            success: false,
                            message: 'No text could be extracted from the image. Please try a clearer image.'
                        });
                    }
                } else {
                    reject({
                        success: false,
                        message: 'No text could be extracted from the image. Please try a clearer image.'
                    });
                }
            })
            .catch((error) => {
                if (progressCallback) {
                    progressCallback(0);
                }

                let errorMessage = 'OCR processing failed. Please try again.';
                
                // Handle timeout error specifically
                if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
                    errorMessage = 'Processing took too long. This can happen with:\n• Complex handwritten documents\n• Large image files\n• First-time initialization\n\nPlease try a clearer image or check your backend is running.';
                } else if (error.response?.data?.message) {
                    errorMessage = error.response.data.message;
                } else if (error.response?.data?.detail) {
                    errorMessage = error.response.data.detail;
                } else if (error.message) {
                    errorMessage = error.message;
                }
                
                reject({
                    success: false,
                    message: `OCR processing failed: ${errorMessage}`
                });
            });
    });
};

/**
 * Clean and format extracted text
 * @param {string} text - Raw extracted text
 * @returns {string} Formatted text
 */
export const formatExtractedText = (text) => {
    if (!text) return '';

    return text
        // Remove excessive whitespace
        .replace(/\s+/g, ' ')
        // Add line breaks after common medical abbreviations
        .replace(/(mg|ml|tablet|capsule|tablet\.|capsule\.|daily|twice|once|bd|od|td|mg\/ml)/gi, '$&\n')
        // Clean up the text
        .trim();
};

/**
 * Download extracted text as a file
 * @param {string} text - Text to download
 * @param {string} filename - Optional filename
 */
export const downloadText = (text, filename = 'prescription.txt') => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
};

/**
 * Download prescription report with OCR accuracy and validation details
 * @param {string} extractedText - Extracted prescription text
 * @param {object} accuracyData - Accuracy info {accuracy, report, confidence_details}
 * @param {string} filename - Optional filename
 */
export const downloadPrescriptionReport = (extractedText, accuracyData = null, filename = 'prescription_report.txt') => {
    let reportContent = '';
    
    // Report header
    reportContent += '================================================\n';
    reportContent += '              PRESCRIPTION REPORT\n';
    reportContent += '================================================\n\n';
    
    // Timestamp
    const now = new Date();
    reportContent += `Generated: ${now.toLocaleString()}\n\n`;
    
    // OCR Quality Section
    if (accuracyData) {
        reportContent += '------------------------------------------------\n';
        reportContent += 'OCR QUALITY ASSESSMENT\n';
        reportContent += '------------------------------------------------\n';
        reportContent += `Accuracy: ${accuracyData.accuracy}%\n`;
        reportContent += `Assessment: ${accuracyData.report}\n`;
        
        if (accuracyData.confidence_details) {
            reportContent += `Confidence Level: ${accuracyData.confidence_details.confidence_level || 'N/A'}\n`;
            
            if (accuracyData.confidence_details.issues && 
                Array.isArray(accuracyData.confidence_details.issues) && 
                accuracyData.confidence_details.issues.length > 0) {
                reportContent += 'Identified Issues:\n';
                accuracyData.confidence_details.issues.forEach(issue => {
                    reportContent += `  - ${issue}\n`;
                });
            }
        }
        reportContent += '\n';
    }
    
    // Extracted Text Section
    reportContent += '------------------------------------------------\n';
    reportContent += 'EXTRACTED PRESCRIPTION TEXT\n';
    reportContent += '------------------------------------------------\n';
    reportContent += extractedText || '[No text extracted]';
    reportContent += '\n\n';
    
    // Footer
    reportContent += '================================================\n';
    reportContent += 'This report was generated by MediAI OCR Service\n';
    reportContent += '================================================\n';
    
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
};

/**
 * Get AI diagnosis and analysis of extracted prescription text
 * Uses dedicated prescription analysis API endpoint
 * @param {string} extractedText - The OCR-extracted prescription text
 * @param {string} patientName - Optional patient name
 * @param {number} patientAge - Optional patient age
 * @param {string} patientId - Optional patient ID
 * @returns {Promise} Promise with detailed prescription analysis
 */
export const getAIDiagnosis = (extractedText, patientName = null, patientAge = null, patientId = null) => {
    return new Promise((resolve, reject) => {
        if (!extractedText || extractedText.trim().length === 0) {
            reject({ success: false, message: 'No text to analyze' });
            return;
        }

        axios.post(`${API_URL}/api/analyze-prescription`, {
            extracted_text: extractedText,
            patient_name: patientName,
            patient_age: patientAge,
            patient_id: patientId
        }, {
            timeout: 120000
        })
            .then((response) => {
                const data = response.data;
                
                // Format analysis report from structured response
                let analysisReport = '';
                
                analysisReport += '========================================\n';
                analysisReport += 'PRESCRIPTION ANALYSIS REPORT\n';
                analysisReport += '========================================\n\n';
                
                // Patient Information
                analysisReport += '[PATIENT INFORMATION]\n';
                analysisReport += '----------------------------------------\n';
                analysisReport += `Name: ${data.patient_info.name}\n`;
                analysisReport += `Age: ${data.patient_info.age}\n`;
                analysisReport += `ID: ${data.patient_info.id}\n`;
                analysisReport += `Date: ${data.patient_info.date}\n\n`;
                
                // Medications
                analysisReport += '[MEDICATIONS IDENTIFIED]\n';
                analysisReport += '----------------------------------------\n';
                if (data.extracted_medications && data.extracted_medications.length > 0) {
                    data.extracted_medications.forEach((med, idx) => {
                        analysisReport += `\n${idx + 1}. ${med.name}\n`;
                        analysisReport += `   Dosage: ${med.dosage || 'Not specified'}\n`;
                        analysisReport += `   Frequency: ${med.frequency || 'Not specified'}\n`;
                        analysisReport += `   Purpose: ${med.purpose || 'Not specified'}\n`;
                        if (med.side_effects) analysisReport += `   Side Effects: ${med.side_effects}\n`;
                        if (med.contraindications) analysisReport += `   Contraindications: ${med.contraindications}\n`;
                    });
                    analysisReport += '\n';
                } else {
                    analysisReport += 'No medications identified in the document.\n\n';
                }
                
                // Conditions
                analysisReport += '[DIAGNOSED CONDITIONS]\n';
                analysisReport += '----------------------------------------\n';
                if (data.diagnosed_conditions && data.diagnosed_conditions.length > 0) {
                    data.diagnosed_conditions.forEach((condition, idx) => {
                        analysisReport += `${idx + 1}. ${condition}\n`;
                    });
                    analysisReport += '\n';
                } else {
                    analysisReport += 'No specific conditions identified.\n\n';
                }
                
                // Summary
                analysisReport += '[SUMMARY]\n';
                analysisReport += '----------------------------------------\n';
                analysisReport += `${data.analysis_summary}\n\n`;
                
                // Confidence Score
                analysisReport += `Confidence Score: ${(data.confidence_score * 100).toFixed(1)}%\n`;
                analysisReport += '========================================\n';
                
                resolve({
                    success: true,
                    analysis: analysisReport,
                    structured_data: data
                });
            })
            .catch((error) => {
                const errorMessage = error.response?.data?.detail ||
                    error.response?.data?.message ||
                    error.message ||
                    'Prescription analysis unavailable';

                reject({
                    success: false,
                    message: `Analysis failed: ${errorMessage}`
                });
            });
    });
};
