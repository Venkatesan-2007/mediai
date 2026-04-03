import React from 'react';

/**
 * SearchBar Component
 * Search input for filtering books by name, subject, or topic
 * @param {string} searchTerm - Current search term
 * @param {Function} onSearch - Handler for search input changes
 */
const SearchBar = ({ searchTerm, onSearch }) => {
    return (
        <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </div>
            <input
                type="text"
                value={searchTerm}
                onChange={(e) => onSearch(e.target.value)}
                placeholder="Search by book name, subject, or topic..."
                className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:border-gray-400 focus:outline-none transition-colors text-gray-700 placeholder-gray-400 bg-white"
            />
            {searchTerm && (
                <button
                    onClick={() => onSearch('')}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            )}
        </div>
    );
};

export default SearchBar;
