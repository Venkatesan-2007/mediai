/**
 * Dashboard Configuration
 * Central configuration file for dashboard feature
 */

// Feature Configuration
export const DASHBOARD_CONFIG = {
    // Feature is enabled
    enabled: true,
    
    // Dashboard refresh interval (in milliseconds)
    refreshInterval: 5 * 60 * 1000, // 5 minutes
    
    // Enable/disable specific features
    features: {
        progressChart: true,
        dashboardCards: true,
        recommendationSection: true,
        weakAreasAnalysis: true,
    },
    
    // Chart and visualization settings
    chart: {
        animationDuration: 300,
        animationDelay: 100,
        enableTransitions: true,
    },
    
    // Theme configuration
    theme: {
        primaryColor: '#ec4899',
        primaryDark: '#db2777',
        primaryLight: '#f472b6',
        secondaryColor: '#fce7f3',
        accentColor: '#db2777',
    },
    
    // Data settings
    data: {
        maxRecentTopics: 5,
        maxUpcomingExams: 4,
        maxRecommendedTopics: 5,
        maxWeakAreas: 3,
        maxAccessedBooks: 5,
        maxHighYieldTopics: 5,
    },
    
    // API settings
    api: {
        timeout: 10000, // 10 seconds
        retryAttempts: 3,
        retryDelay: 1000, // 1 second
    },
    
    // Error handling
    errorHandling: {
        showErrorBoundary: true,
        logErrors: true,
        enableFallback: true,
    },
};

export default DASHBOARD_CONFIG;
