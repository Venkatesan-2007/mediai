import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../../shared/components/Navbar';
import DashboardCards from '../components/DashboardCards';
import ProgressChart from '../components/ProgressChart';
import { useAuth } from '../../../shared/contexts/AuthContext';
import axios from 'axios';

/**
 * Dashboard Page Component
 * Student dashboard with progress overview, topics, exams, and analytics
 */
const Dashboard = () => {
    const navigate = useNavigate();
    const { logout, token } = useAuth();
    // Dashboard state
    const [studentData, setStudentData] = useState({
        progress: 0,
        recentTopics: [],
        upcomingExams: [],
        questionsToday: 0,
        recommendedTopics: [],
        weakAreas: []
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Load real dashboard data from API
    useEffect(() => {
        const loadDashboardData = async () => {
            try {
                setLoading(true);
                setError(null);
                
                // Get user stats from API
                const response = await axios.get('http://localhost:8000/api/user-stats', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                const stats = response.data;
                
                // Transform API data to dashboard format
                setStudentData({
                    progress: stats.progress_score,
                    recentTopics: [
                        { id: 1, name: 'Medical Documents', date: new Date().toISOString().split('T')[0] },
                        { id: 2, name: 'Clinical Cases', date: new Date(Date.now() - 86400000).toISOString().split('T')[0] }
                    ],
                    upcomingExams: [
                        { id: 1, name: 'Medical Knowledge Test', subject: 'General Medicine', date: '2026-03-01', daysLeft: 7 }
                    ],
                    questionsToday: stats.recent_activity,
                    recommendedTopics: [
                        { id: 1, name: 'Advanced Diagnostics', reason: 'Based on your activity' },
                        { id: 2, name: 'Clinical Procedures', reason: 'Popular topic' }
                    ],
                    weakAreas: [
                        { id: 1, subject: 'Document Analysis', score: Math.max(0, 100 - stats.average_rating * 20), suggestion: 'Upload more medical documents' },
                        { id: 2, subject: 'Question Quality', score: stats.average_rating * 20, suggestion: 'Ask more specific questions' }
                    ]
                });
                
            } catch (err) {
                console.error('Failed to load dashboard data:', err);
                setError('Failed to load dashboard data. Please try again.');
                
                // Fallback to basic data
                setStudentData({
                    progress: 25,
                    recentTopics: [{ id: 1, name: 'Getting Started', date: new Date().toISOString().split('T')[0] }],
                    upcomingExams: [],
                    questionsToday: 0,
                    recommendedTopics: [{ id: 1, name: 'Upload Documents', reason: 'Start your learning journey' }],
                    weakAreas: [{ id: 1, subject: 'Setup', score: 25, suggestion: 'Complete your profile setup' }]
                });
            } finally {
                setLoading(false);
            }
        };
        
        if (token) {
            loadDashboardData();
        }
    }, [token]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-pink flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-pink-300 border-t-pink-600 rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading your dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-pink flex items-center justify-center">
                <div className="text-center max-w-md mx-auto p-6">
                    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                    </div>
                    <h2 className="text-xl font-semibold text-gray-800 mb-2">Unable to Load Dashboard</h2>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-6 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-pink flex flex-col">
            <Navbar onLogout={logout} />

            <main className="flex-1 container mx-auto px-4 py-6 max-w-7xl">
                {/* Page Header */}
                <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-800">Student Dashboard</h1>
                        <p className="text-gray-500 mt-1">Track your progress and optimize your study plan</p>
                    </div>
                    <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row gap-3">
                        <button
                            onClick={() => window.location.reload()}
                            className="flex items-center justify-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            <span>Refresh</span>
                        </button>
                    </div>
                </div>

                {/* Dashboard Cards */}
                <DashboardCards
                    progress={studentData.progress}
                    questionsToday={studentData.questionsToday}
                    upcomingExams={studentData.upcomingExams}
                />

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                    {/* Progress Chart */}
                    <div className="card-soft p-6 animate-slide-in">
                        <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                            <svg className="w-6 h-6 mr-2 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            Progress Overview
                        </h2>
                        <ProgressChart progress={studentData.progress} />
                    </div>

                    {/* Recent Topics */}
                    <div className="card-soft p-6 animate-slide-in delay-100">
                        <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                            <svg className="w-6 h-6 mr-2 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                            Recent Topics Studied
                        </h2>
                        <div className="space-y-3">
                            {studentData.recentTopics.map((topic, index) => (
                                <div key={topic.id} className="flex items-center justify-between p-3 bg-pink-50 rounded-xl hover:bg-pink-100 transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-8 h-8 bg-pink-200 rounded-lg flex items-center justify-center">
                                            <span className="text-pink-600 font-medium text-sm">{index + 1}</span>
                                        </div>
                                        <span className="text-gray-700 font-medium">{topic.name}</span>
                                    </div>
                                    <span className="text-gray-400 text-sm">{topic.date}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Recommended Topics */}
                    <div className="card-soft p-6 animate-slide-in delay-200">
                        <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                            <svg className="w-6 h-6 mr-2 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                            </svg>
                            Recommended Topics
                        </h2>
                        <div className="space-y-3">
                            {studentData.recommendedTopics.map((topic) => (
                                <div key={topic.id} className="p-4 bg-gradient-to-r from-pink-50 to-white rounded-xl border border-pink-100 hover:shadow-soft transition-shadow">
                                    <div className="flex items-center justify-between">
                                        <span className="text-gray-800 font-medium">{topic.name}</span>
                                        <span className="text-pink-500 text-sm">✨</span>
                                    </div>
                                    <p className="text-gray-500 text-sm mt-1">{topic.reason}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Weak Area Analysis */}
                    <div className="card-soft p-6 animate-slide-in delay-300">
                        <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                            <svg className="w-6 h-6 mr-2 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            Weak Area Analysis
                        </h2>
                        <div className="space-y-4">
                            {studentData.weakAreas.map((area) => (
                                <div key={area.id} className="p-4 bg-red-50 rounded-xl border border-red-100">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-gray-800 font-medium">{area.subject}</span>
                                        <span className="text-red-500 font-bold">{area.score}%</span>
                                    </div>
                                    <div className="w-full bg-red-200 rounded-full h-2 mb-2">
                                        <div
                                            className="bg-red-400 h-2 rounded-full"
                                            style={{ width: `${area.score}%` }}
                                        ></div>
                                    </div>
                                    <p className="text-gray-500 text-sm">💡 {area.suggestion}</p>
                                </div>
                            ))}
                        </div>
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

export default Dashboard;
