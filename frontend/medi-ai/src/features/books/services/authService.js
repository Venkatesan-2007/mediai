/**
 * Authentication & Chat Service - Backend API Integration
 * Handles user authentication and API requests with JWT tokens
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const CURRENT_USER_KEY = 'current_user';

/**
 * Get authorization headers with JWT token
 * @returns {Object} Headers object with auth token if available
 */
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
};

/**
 * Get authorization headers for multipart form data (file uploads)
 * @returns {Object} Headers object with auth token if available (no Content-Type for FormData)
 */
const getFormDataHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
};

// ============================================================================
// CHAT ENDPOINT
// ============================================================================

/**
 * Send chat message to backend
 * @param {string} question - User's question
 * @returns {Promise} Response from API
 */
export const sendMessage = async (question) => {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error(`Chat error: ${response.statusText}`);
  }

  return response.json();
};

// ============================================================================
// PDF UPLOAD ENDPOINTS
// ============================================================================

/**
 * Upload a PDF file
 * @param {File} file - PDF file to upload
 * @returns {Promise} Response from API
 */
export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/api/upload-pdf`, {
    method: 'POST',
    headers: getFormDataHeaders(),
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get list of uploaded PDFs for current user
 * @returns {Promise} Response containing list of books
 */
export const getUploadedBooks = async () => {
  const response = await fetch(`${API_URL}/api/uploaded-pdfs`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
};

// ============================================================================
// STATUS ENDPOINT
// ============================================================================

/**
 * Get system status
 * @returns {Promise} Response containing status information
 */
export const getStatus = async () => {
  const response = await fetch(`${API_URL}/api/status`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get current logged-in user from localStorage
 * @returns {Object|null} User object or null if not logged in
 */
export const getCurrentUser = () => {
    const user = localStorage.getItem(CURRENT_USER_KEY);
    return user ? JSON.parse(user) : null;
};

/**
 * Check if user is authenticated
 * @returns {boolean} True if user is logged in
 */
export const isAuthenticated = () => {
    return getCurrentUser() !== null;
};
