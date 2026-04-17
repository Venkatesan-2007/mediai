/**
 * Custom Hook: useDashboardData
 * Manages dashboard data fetching and state management
 * Handles API calls, error handling, and data transformation
 */

import { useState, useEffect } from 'react';
import {
    DASHBOARD_API_ENDPOINTS,
    DEFAULT_DASHBOARD_DATA,
    LOADING_STATES,
} from '../constants/dashboardConstants';

/**
 * Hook to fetch and manage dashboard data
 * @param {string} token - Authentication token
 * @returns {Object} Dashboard data, loading state, and error
 */
export const useDashboardData = (token) => {
    const [studentData, setStudentData] = useState(DEFAULT_DASHBOARD_DATA);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [loadingState, setLoadingState] = useState(LOADING_STATES.IDLE);

    /**
     * Fetch dashboard data from API
     */
    const loadDashboardData = async () => {
        try {
            setLoading(true);
            setLoadingState(LOADING_STATES.LOADING);
            setError(null);

            // Fetch user stats from API
            const response = await fetch(DASHBOARD_API_ENDPOINTS.USER_STATS, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const stats = await response.json();

            // Transform API data to dashboard format
            const transformedData = {
                progress: stats.progress_score || 0,
                recentTopics: [
                    { id: 1, name: 'Medical Documents', date: new Date().toISOString().split('T')[0] },
                    { id: 2, name: 'Clinical Cases', date: new Date(Date.now() - 86400000).toISOString().split('T')[0] }
                ],
                upcomingExams: [
                    { id: 1, name: 'Medical Knowledge Test', subject: 'General Medicine', date: '2026-03-01', daysLeft: 7 }
                ],
                questionsToday: stats.recent_activity || 0,
                recommendedTopics: [
                    { id: 1, name: 'Advanced Diagnostics', reason: 'Based on your activity' },
                    { id: 2, name: 'Clinical Procedures', reason: 'Popular topic' }
                ],
                weakAreas: [
                    { id: 1, subject: 'Document Analysis', score: Math.max(0, 100 - (stats.average_rating || 0) * 20), suggestion: 'Upload more medical documents' },
                    { id: 2, subject: 'Question Quality', score: (stats.average_rating || 0) * 20, suggestion: 'Ask more specific questions' }
                ]
            };

            setStudentData(transformedData);
            setLoadingState(LOADING_STATES.SUCCESS);
        } catch (err) {
            console.error('Failed to load dashboard data:', err);
            setError('Failed to load dashboard data. Please try again.');
            setLoadingState(LOADING_STATES.ERROR);

            // Fallback to default data
            setStudentData({
                ...DEFAULT_DASHBOARD_DATA,
                progress: 25,
                recentTopics: [{ id: 1, name: 'Getting Started', date: new Date().toISOString().split('T')[0] }],
                recommendedTopics: [{ id: 1, name: 'Upload Documents', reason: 'Start your learning journey' }],
                weakAreas: [{ id: 1, subject: 'Setup', score: 25, suggestion: 'Complete your profile setup' }]
            });
        } finally {
            setLoading(false);
        }
    };

    /**
     * Refresh dashboard data
     */
    const refreshData = async () => {
        await loadDashboardData();
    };

    useEffect(() => {
        if (token) {
            loadDashboardData();
        }
    }, [token]);

    return {
        studentData,
        loading,
        error,
        loadingState,
        refreshData,
    };
};

export default useDashboardData;
