import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Navbar Component
 * Top navigation bar with logo, menu items, and logout functionality
 */
const Navbar = ({ onLogout }) => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user } = useAuth();

    /**
     * Handle logout and redirect to login
     */
    const handleLogout = () => {
        if (onLogout) {
            onLogout();
        }
        navigate('/login');
    };

    /**
     * Check if current route is active
     * @param {string} path - Route path
     * @returns {boolean} True if route is active
     */
    const isActive = (path) => location.pathname === path;

    return (
        <nav className="bg-white/90 backdrop-blur-md shadow-soft sticky top-0 z-50 border-b border-pink-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo Section */}
                    <div className="flex-shrink-0 flex items-center">
                        <Link to="/chat" className="flex items-center space-x-2 group">
                            <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-pink-600 rounded-xl flex items-center justify-center shadow-soft group-hover:scale-110 transition-transform duration-300">
                                <svg
                                    className="w-6 h-6 text-white"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                                    />
                                </svg>
                            </div>
                            <span className="text-xl font-bold text-gradient">Medi AI</span>
                        </Link>
                    </div>

                    {/* Navigation Links */}
                    <div className="hidden md:flex items-center space-x-2">
                        <Link
                            to="/dashboard"
                            className={`px-4 py-2 rounded-xl font-medium transition-all duration-300 ${isActive('/dashboard')
                                ? 'bg-pink-100 text-pink-600'
                                : 'text-gray-600 hover:bg-pink-50 hover:text-pink-600'
                                }`}
                        >
                            <div className="flex items-center space-x-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                                </svg>
                                <span>Dashboard</span>
                            </div>
                        </Link>

                        <Link
                            to="/booklist"
                            className={`px-4 py-2 rounded-xl font-medium transition-all duration-300 ${isActive('/booklist')
                                ? 'bg-pink-100 text-pink-600'
                                : 'text-gray-600 hover:bg-pink-50 hover:text-pink-600'
                                }`}
                        >
                            <span>Booklist</span>
                        </Link>

                        <Link
                            to="/questions"
                            className={`px-4 py-2 rounded-xl font-medium transition-all duration-300 ${isActive('/questions')
                                ? 'bg-pink-100 text-pink-600'
                                : 'text-gray-600 hover:bg-pink-50 hover:text-pink-600'
                                }`}
                        >
                            <span>AI Question Builder</span>
                        </Link>

                        <Link
                            to="/chat"
                            className={`px-4 py-2 rounded-xl font-medium transition-all duration-300 ${isActive('/chat')
                                ? 'bg-pink-100 text-pink-600'
                                : 'text-gray-600 hover:bg-pink-50 hover:text-pink-600'
                                }`}
                        >
                            <div className="flex items-center space-x-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                </svg>
                                <span>Chat</span>
                            </div>
                        </Link>

                        <Link
                            to="/signature-analysis"
                            className={`px-4 py-2 rounded-xl font-medium transition-all duration-300 ${isActive('/signature-analysis')
                                ? 'bg-pink-100 text-pink-600'
                                : 'text-gray-600 hover:bg-pink-50 hover:text-pink-600'
                                }`}
                        >
                            <div className="flex items-center space-x-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <span>Signature Analysis</span>
                            </div>
                        </Link>
                    </div>

                    {/* User Section */}
                    <div className="flex items-center space-x-4">
                        {/* User Info */}
                        {user && user.name && (
                            <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 bg-pink-50 rounded-full">
                                <div className="w-8 h-8 bg-gradient-to-br from-pink-400 to-pink-600 rounded-full flex items-center justify-center">
                                    <span className="text-white font-medium text-sm">
                                        {user.name.charAt(0).toUpperCase()}
                                    </span>
                                </div>
                                <span className="text-sm font-medium text-gray-700">{user.name}</span>
                            </div>
                        )}

                        {/* Logout Button */}
                        <button
                            onClick={handleLogout}
                            className="flex items-center space-x-2 px-4 py-2 bg-pink-100 text-pink-600 rounded-xl font-medium hover:bg-pink-200 transition-all duration-300 hover:scale-105"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                            </svg>
                            <span className="hidden sm:inline">Logout</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation */}
            <div className="md:hidden border-t border-pink-100">
                <div className="flex justify-around py-2">
                    <Link
                        to="/dashboard"
                        className={`flex flex-col items-center px-3 py-2 rounded-lg ${isActive('/dashboard') ? 'text-pink-600' : 'text-gray-500'
                            }`}
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                        </svg>
                        <span className="text-xs mt-1">Dashboard</span>
                    </Link>
                    <Link
                        to="/chat"
                        className={`flex flex-col items-center px-3 py-2 rounded-lg ${isActive('/chat') ? 'text-pink-600' : 'text-gray-500'
                            }`}
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <span className="text-xs mt-1">Chat</span>
                    </Link>
                    <Link
                        to="/signature-analysis"
                        className={`flex flex-col items-center px-3 py-2 rounded-lg ${isActive('/signature-analysis') ? 'text-pink-600' : 'text-gray-500'
                            }`}
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="text-xs mt-1">Signature</span>
                    </Link>
                    <button
                        onClick={handleLogout}
                        className="flex flex-col items-center px-3 py-2 text-gray-500"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        <span className="text-xs mt-1">Logout</span>
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
