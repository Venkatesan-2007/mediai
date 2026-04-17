/**
 * Dashboard Utility Functions
 * Helper functions for data manipulation and formatting
 */

/**
 * Calculate progress percentage between two values
 * @param {number} current - Current value
 * @param {number} total - Total value
 * @returns {number} Progress percentage
 */
export const calculateProgress = (current, total) => {
    if (total === 0) return 0;
    return Math.round((current / total) * 100);
};

/**
 * Format date to readable string
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date string
 */
export const formatDate = (date) => {
    if (typeof date === 'string') {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

/**
 * Calculate days remaining until a specific date
 * @param {string|Date} targetDate - Target date
 * @returns {number} Days remaining
 */
export const calculateDaysRemaining = (targetDate) => {
    const target = new Date(targetDate);
    const today = new Date();
    const difference = target.getTime() - today.getTime();
    return Math.ceil(difference / (1000 * 3600 * 24));
};

/**
 * Find the nearest exam from a list of exams
 * @param {Array} exams - Array of exam objects
 * @returns {Object|null} Nearest exam or null if no exams
 */
export const findNearestExam = (exams) => {
    if (!exams || exams.length === 0) return null;

    return exams.reduce((nearest, exam) => {
        return exam.daysLeft < nearest.daysLeft ? exam : nearest;
    }, exams[0]);
};

/**
 * Sort topics by importance
 * @param {Array} topics - Array of topic objects
 * @returns {Array} Sorted topics array
 */
export const sortTopicsByImportance = (topics) => {
    const importanceOrder = { 'High': 1, 'Medium': 2, 'Low': 3 };
    return [...topics].sort((a, b) => {
        return (importanceOrder[a.importance] || 999) - (importanceOrder[b.importance] || 999);
    });
};

/**
 * Sort books by view count (descending)
 * @param {Array} books - Array of book objects
 * @returns {Array} Sorted books array
 */
export const sortBooksByViews = (books) => {
    return [...books].sort((a, b) => b.views - a.views);
};

/**
 * Get performance level based on score
 * @param {number} score - Score value (0-100)
 * @returns {string} Performance level
 */
export const getPerformanceLevel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Need Improvement';
};

/**
 * Get performance color based on score (for UI)
 * @param {number} score - Score value (0-100)
 * @returns {string} Tailwind color class
 */
export const getPerformanceColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 60) return 'text-orange-600';
    return 'text-pink-600';
};

/**
 * Format large numbers with abbreviations (e.g., 1000 -> 1K)
 * @param {number} num - Number to format
 * @returns {string} Formatted number string
 */
export const formatLargeNumber = (num) => {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
};

/**
 * Validate dashboard data structure
 * @param {Object} data - Data object to validate
 * @returns {boolean} True if data is valid
 */
export const validateDashboardData = (data) => {
    if (!data) return false;
    
    return (
        typeof data.progress === 'number' &&
        Array.isArray(data.recentTopics) &&
        Array.isArray(data.upcomingExams) &&
        typeof data.questionsToday === 'number' &&
        Array.isArray(data.recommendedTopics) &&
        Array.isArray(data.weakAreas)
    );
};

/**
 * Merge two dashboard data objects
 * @param {Object} oldData - Old data
 * @param {Object} newData - New data
 * @returns {Object} Merged data
 */
export const mergeDashboardData = (oldData, newData) => {
    return {
        ...oldData,
        ...newData,
    };
};

export default {
    calculateProgress,
    formatDate,
    calculateDaysRemaining,
    findNearestExam,
    sortTopicsByImportance,
    sortBooksByViews,
    getPerformanceLevel,
    getPerformanceColor,
    formatLargeNumber,
    validateDashboardData,
    mergeDashboardData,
};
