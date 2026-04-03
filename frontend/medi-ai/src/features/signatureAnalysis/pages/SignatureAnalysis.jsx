import React, { useState } from 'react';
import Navbar from '../../../shared/components/Navbar';
import ImageUploader from '../components/ImageUploader';
import { useAuth } from '../../../shared/contexts/AuthContext';
import { extractTextFromImage, downloadPrescriptionReport, getAIDiagnosis } from '../services/ocrService';

/**
 * Signature Analysis Page Component
 * Handles prescription/signature OCR and text extraction with AI diagnosis
 */
const SignatureAnalysis = () => {
    const { logout } = useAuth();
    const [selectedImage, setSelectedImage] = useState(null);
    const [extractedText, setExtractedText] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [accuracyData, setAccuracyData] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [aiAnalysis, setAiAnalysis] = useState('');
    const [analysisError, setAnalysisError] = useState('');
    
    // Patient information (optional)
    const [patientName, setPatientName] = useState('');
    const [patientAge, setPatientAge] = useState('');
    const [patientId, setPatientId] = useState('');

    /**
     * Handle image selection
     * @param {File} file - Selected image file
     */
    const handleImageSelect = (file) => {
        setSelectedImage(file);
        setExtractedText('');
        setError('');
        setSuccess('');
        setAccuracyData(null);
        setAiAnalysis('');
        setAnalysisError('');
    };

    /**
     * Process the image and extract text
     */
    const handleConvertToText = async () => {
        if (!selectedImage) {
            setError('Please select an image first');
            return;
        }

        setIsProcessing(true);
        setProgress(0);
        setError('');
        setSuccess('');
        setAiAnalysis('');
        setAnalysisError('');

        try {
            const result = await extractTextFromImage(selectedImage, (p) => {
                setProgress(p);
            });

            if (result.success) {
                setExtractedText(result.text);
                // Store accuracy data but don't display in UI (for prescription report)
                setAccuracyData({
                    accuracy: result.accuracy,
                    report: result.report,
                    confidence_details: result.confidence_details
                });
                setSuccess('Text extracted successfully!');
                
                // Auto-start AI analysis
                performAIDiagnosis(result.text);
            }
        } catch (err) {
            setError(err.message || 'Failed to extract text from image');
        } finally {
            setIsProcessing(false);
            setProgress(0);
        }
    };

    /**
     * Perform AI diagnosis on extracted text
     */
    const performAIDiagnosis = async (textToAnalyze) => {
        setIsAnalyzing(true);
        setAnalysisError('');
        
        try {
            const result = await getAIDiagnosis(
                textToAnalyze,
                patientName || null,
                patientAge ? parseInt(patientAge) : null,
                patientId || null
            );
            if (result.success) {
                setAiAnalysis(result.analysis);
            }
        } catch (err) {
            setAnalysisError(err.message || 'Failed to generate AI analysis. Please ensure backend is running.');
        } finally {
            setIsAnalyzing(false);
        }
    };

    /**
     * Handle download of prescription report with accuracy
     */
    const handleDownload = () => {
        if (extractedText) {
            downloadPrescriptionReport(extractedText, accuracyData, 'prescription_report.txt');
        }
    };

    /**
     * Handle reset/clear
     */
    const handleReset = () => {
        setSelectedImage(null);
        setExtractedText('');
        setError('');
        setSuccess('');
        setProgress(0);
        setAccuracyData(null);
        setAiAnalysis('');
        setAnalysisError('');
        setIsAnalyzing(false);
        setPatientName('');
        setPatientAge('');
        setPatientId('');
    };

    return (
        <div className="min-h-screen bg-gradient-pink flex flex-col">
            <Navbar onLogout={logout} />

            <main className="flex-1 container mx-auto px-4 py-6 max-w-4xl">
                {/* Page Header */}
                <div className="text-center mb-8">
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">Prescription OCR & AI Diagnosis</h1>
                    <p className="text-gray-500 mt-2">
                        Upload a prescription image to extract text and get AI-powered medical analysis
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Left Column - Upload */}
                    <div className="card-soft p-6 animate-slide-in">
                        <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                            <svg className="w-6 h-6 mr-2 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            Upload Image
                        </h2>

                        <ImageUploader onImageSelect={handleImageSelect} disabled={isProcessing} />

                        {/* Optional Patient Information */}
                        <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
                            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                                <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Patient Information (Optional)
                            </h3>
                            <div className="space-y-2">
                                <input
                                    type="text"
                                    placeholder="Patient Name"
                                    value={patientName}
                                    onChange={(e) => setPatientName(e.target.value)}
                                    disabled={isProcessing}
                                    className="w-full px-3 py-2 rounded-lg border border-blue-300 bg-white/70 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none text-sm"
                                />
                                <input
                                    type="number"
                                    placeholder="Patient Age"
                                    value={patientAge}
                                    onChange={(e) => setPatientAge(e.target.value)}
                                    disabled={isProcessing}
                                    className="w-full px-3 py-2 rounded-lg border border-blue-300 bg-white/70 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none text-sm"
                                />
                                <input
                                    type="text"
                                    placeholder="Patient ID"
                                    value={patientId}
                                    onChange={(e) => setPatientId(e.target.value)}
                                    disabled={isProcessing}
                                    className="w-full px-3 py-2 rounded-lg border border-blue-300 bg-white/70 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none text-sm"
                                />
                            </div>
                        </div>

                        {/* Convert Button */}
                        <div className="mt-6">
                            <button
                                onClick={handleConvertToText}
                                disabled={!selectedImage || isProcessing}
                                className={`btn-primary w-full flex items-center justify-center ${!selectedImage || isProcessing ? 'opacity-50 cursor-not-allowed' : ''
                                    }`}
                            >
                                {isProcessing ? (
                                    <>
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Processing... {progress}%
                                    </>
                                ) : (
                                    <>
                                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        Convert to Text
                                    </>
                                )}
                            </button>

                            {/* Progress Bar */}
                            {isProcessing && (
                                <div className="mt-4">
                                    <div className="w-full bg-pink-100 rounded-full h-2">
                                        <div
                                            className="bg-gradient-to-r from-pink-500 to-pink-600 h-2 rounded-full transition-all duration-300"
                                            style={{ width: `${progress}%` }}
                                        ></div>
                                    </div>
                                    <p className="text-center text-sm text-gray-500 mt-2">
                                        Analyzing image... {progress}%
                                    </p>
                                    {progress > 30 && (
                                        <p className="text-center text-xs text-gray-400 mt-2">
                                            This may take up to 3 minutes for complex handwritten documents
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Column - Result */}
                    <div className="card-soft p-6 animate-slide-in delay-200">
                        <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                            <svg className="w-6 h-6 mr-2 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            Extracted Text
                        </h2>

                        {/* Error Message */}
                        {error && (
                            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm flex items-center">
                                <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                {error}
                            </div>
                        )}

                        {/* Success Message */}
                        {success && (
                            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-xl text-green-600 text-sm flex items-center">
                                <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                {success}
                            </div>
                        )}

                        {/* Text Output */}
                        <div className="relative">
                            <textarea
                                value={extractedText}
                                onChange={(e) => setExtractedText(e.target.value)}
                                placeholder="Extracted text will appear here..."
                                className="w-full h-64 sm:h-80 px-4 py-3 rounded-xl border-2 border-pink-200 bg-white/50 focus:border-pink-400 focus:ring-4 focus:ring-pink-100 focus:outline-none transition-all duration-300 resize-none text-gray-700 placeholder-pink-300"
                                disabled={isProcessing}
                            />

                            {extractedText && (
                                <div className="absolute bottom-3 right-3 flex space-x-2">
                                    <button
                                        onClick={handleDownload}
                                        className="p-2 bg-pink-100 text-pink-600 rounded-lg hover:bg-pink-200 transition-colors"
                                        title="Download report"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                        </svg>
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Action Buttons */}
                        {extractedText && (
                            <div className="mt-4 flex space-x-3">
                                <button
                                    onClick={handleReset}
                                    className="btn-secondary flex-1"
                                >
                                    Start Over
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* AI Diagnosis Section */}
                {(isAnalyzing || aiAnalysis) && (
                    <div className="mt-6 card-soft p-6 animate-slide-in">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-semibold text-gray-700 flex items-center">
                                <svg className="w-6 h-6 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                                AI Medical Analysis Report
                            </h2>
                            {isAnalyzing && (
                                <div className="flex items-center space-x-2">
                                    <svg className="animate-spin h-5 w-5 text-purple-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    <span className="text-purple-600 text-sm font-medium">Analyzing...</span>
                                </div>
                            )}
                        </div>

                        {/* Analysis Error */}
                        {analysisError && (
                            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl text-yellow-700 text-sm flex items-start">
                                <svg className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4v2m0-6a4 4 0 11-8 0 4 4 0 018 0z" />
                                </svg>
                                <div>
                                    <p className="font-semibold mb-1">Analysis Note</p>
                                    <p>{analysisError}</p>
                                </div>
                            </div>
                        )}

                        {/* Analysis Content */}
                        {aiAnalysis && (
                            <div className="bg-purple-50/50 rounded-xl p-4 max-h-96 overflow-y-auto">
                                <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                                    {aiAnalysis}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Info Section */}
                <div className="mt-8 card-glass p-6">
                    <h3 className="text-lg font-semibold text-gray-700 mb-3">How to Use</h3>
                    <ol className="list-decimal list-inside space-y-2 text-gray-600">
                        <li>Upload a prescription image (JPG, PNG, or GIF)</li>
                        <li>Click "Convert to Text" to extract the content</li>
                        <li>The AI will automatically analyze the prescription</li>
                        <li>Review the extracted text and AI diagnosis report</li>
                        <li>Download the comprehensive report for your records</li>
                    </ol>
                    <div className="mt-4 p-3 bg-pink-50 rounded-xl">
                        <p className="text-sm text-pink-600">
                            <strong>Note:</strong> The AI analysis provides medical insights and drug interaction checks. 
                            For best results, use clear, high-resolution images. Always consult with healthcare professionals for medical decisions.
                        </p>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="py-4 text-center text-gray-400 text-sm">
                <p>© 2026 Medi AI - Your Health Assistant</p>
            </footer>
        </div>
    );
};

export default SignatureAnalysis;
