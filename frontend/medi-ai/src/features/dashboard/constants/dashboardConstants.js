/**
 * Dashboard Constants
 * This file contains all constant values used in the Dashboard feature
 */

// API Endpoints
export const DASHBOARD_API_ENDPOINTS = {
    USER_STATS: 'http://localhost:8000/api/user-stats',
    USER_PROGRESS: 'http://localhost:8000/api/user-progress',
};

// Default Dashboard Data
export const DEFAULT_DASHBOARD_DATA = {
    progress: 0,
    recentTopics: [],
    upcomingExams: [],
    questionsToday: 0,
    recommendedTopics: [],
    weakAreas: [],
};

// Dashboard Chart Colors (Pink & White Theme)
export const DASHBOARD_COLORS = {
    primary: '#ec4899', // Pink
    primaryDark: '#db2777', // Dark Pink
    primaryLight: '#f472b6', // Light Pink
    secondary: '#fce7f3', // Very Light Pink
    white: '#ffffff',
    gray: '#6b7280',
    lightGray: '#f3f4f6',
};

// Animation Delays
export const ANIMATION_DELAYS = {
    card1: 0,
    card2: 100,
    card3: 200,
    card4: 300,
};

// Chart Configuration
export const CHART_CONFIG = {
    maxValue: 100,
    barHeight: 128, // h-32 in Tailwind
    animationDuration: 300,
};

// High Yield Topics
export const HIGH_YIELD_TOPICS = [
    { id: 1, topic: "Cardiovascular System", importance: "High" },
    { id: 2, topic: "Respiratory Diseases", importance: "High" },
    { id: 3, topic: "CNS Pharmacology", importance: "High" },
    { id: 4, topic: "Renal Physiology", importance: "Medium" },
    { id: 5, topic: "GI Pathology", importance: "Medium" }
];

// Exam Recommended Chapters
export const EXAM_RECOMMENDED_CHAPTERS = [
    { id: 1, chapter: "Heart Anatomy", book: "Gray's Anatomy", examWeight: "90%" },
    { id: 2, chapter: "ECG Interpretation", book: "Clinical Cardiology", examWeight: "95%" },
    { id: 3, chapter: "Respiratory Failure", book: "Harrison's Principles", examWeight: "88%" },
    { id: 4, chapter: "Diabetes Mellitus", book: "Williams Textbook", examWeight: "92%" }
];

// Most Accessed Books
export const MOST_ACCESSED_BOOKS = [
    { id: 1, title: "Gray's Anatomy", author: "Henry Gray", views: 2453 },
    { id: 2, title: "Harrison's Principles of Internal Medicine", author: "Dennis Kasper", views: 2102 },
    { id: 3, title: "Robbins Pathologic Basis of Disease", author: "Vinay Kumar", views: 1890 },
    { id: 4, title: "Ganong's Review of Medical Physiology", author: "Kim Barrett", views: 1654 }
];

// Error Messages
export const DASHBOARD_ERROR_MESSAGES = {
    FAILED_TO_LOAD: 'Failed to load dashboard data. Please try again.',
    NETWORK_ERROR: 'Network error. Please check your connection.',
    SERVER_ERROR: 'Server error. Please try again later.',
};

// Success Messages
export const DASHBOARD_SUCCESS_MESSAGES = {
    DATA_LOADED: 'Dashboard data loaded successfully.',
    REFRESH_COMPLETE: 'Dashboard refreshed successfully.',
};

// Loading States
export const LOADING_STATES = {
    IDLE: 'idle',
    LOADING: 'loading',
    SUCCESS: 'success',
    ERROR: 'error',
};

export default {
    DASHBOARD_API_ENDPOINTS,
    DEFAULT_DASHBOARD_DATA,
    DASHBOARD_COLORS,
    ANIMATION_DELAYS,
    CHART_CONFIG,
    HIGH_YIELD_TOPICS,
    EXAM_RECOMMENDED_CHAPTERS,
    MOST_ACCESSED_BOOKS,
    DASHBOARD_ERROR_MESSAGES,
    DASHBOARD_SUCCESS_MESSAGES,
    LOADING_STATES,
};
