import React, { useState } from 'react';

/**
 * BookDetailView Component
 * Displays detailed information about a selected book including description, table of contents, and chapter list
 * @param {Object} book - The selected book object
 * @param {Function} onBack - Handler for going back to book list
 * @param {Function} onAskFromBook - Handler for asking questions from a specific chapter
 */
const BookDetailView = ({ book, onBack, onAskFromBook }) => {
    const [selectedChapter, setSelectedChapter] = useState(null);

    if (!book) return null;

    return (
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
            {/* Header with back button */}
            <div className="border-b border-gray-100 p-4">
                <button
                    onClick={onBack}
                    className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    <span>Back to Books</span>
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
                {/* Left Column - Book Info */}
                <div className="lg:col-span-1">
                    {/* Book Cover */}
                    <div className="bg-gray-100 rounded-xl p-4 mb-4">
                        {book.coverImage ? (
                            <img
                                src={book.coverImage}
                                alt={book.title}
                                className="w-full rounded-lg shadow-sm"
                            />
                        ) : (
                            <div className="h-64 bg-gray-200 rounded-lg flex items-center justify-center">
                                <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                </svg>
                            </div>
                        )}
                    </div>

                    {/* Book Details */}
                    <div className="space-y-3">
                        <h1 className="text-xl font-bold text-gray-800">{book.title}</h1>
                        <p className="text-gray-600">{book.author}</p>

                        <div className="flex flex-wrap gap-2 text-sm">
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded">{book.edition}</span>
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded">{book.year}</span>
                            <span className="px-2 py-1 bg-gray-800 text-white rounded">{book.type}</span>
                        </div>

                        <div className="pt-4">
                            <button
                                onClick={() => onAskFromBook(book, selectedChapter)}
                                className="w-full px-4 py-3 bg-gray-800 text-white rounded-xl font-medium hover:bg-gray-900 transition-colors"
                            >
                                Ask from this Book
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right Column - Description & Chapters */}
                <div className="lg:col-span-2">
                    {/* Description */}
                    <div className="mb-6">
                        <h2 className="text-lg font-semibold text-gray-800 mb-3">Description</h2>
                        <p className="text-gray-600 leading-relaxed">
                            {book.description || `This comprehensive medical textbook covers {book.subject} in detail. It is designed for medical students and provides in-depth knowledge with clinical correlations and practical applications.`}
                        </p>
                    </div>

                    {/* Table of Contents */}
                    <div>
                        <h2 className="text-lg font-semibold text-gray-800 mb-3">Table of Contents</h2>
                        <div className="border border-gray-100 rounded-xl overflow-hidden">
                            <div className="max-h-96 overflow-y-auto">
                                {book.chapters && book.chapters.length > 0 ? (
                                    book.chapters.map((chapter, index) => (
                                        <button
                                            key={index}
                                            onClick={() => setSelectedChapter(chapter)}
                                            className={`w-full text-left px-4 py-3 border-b border-gray-50 last:border-b-0 hover:bg-gray-50 transition-colors flex items-center justify-between ${selectedChapter === chapter ? 'bg-gray-100' : ''
                                                }`}
                                        >
                                            <span className="text-gray-700">
                                                <span className="text-gray-400 mr-2">{index + 1}.</span>
                                                {chapter}
                                            </span>
                                            {selectedChapter === chapter && (
                                                <span className="text-xs bg-gray-800 text-white px-2 py-1 rounded">Selected</span>
                                            )}
                                        </button>
                                    ))
                                ) : (
                                    // Default chapters if not provided
                                    [
                                        "Introduction to " + book.subject,
                                        "Basic Principles",
                                        "Anatomy and Physiology",
                                        "Common Conditions",
                                        "Diagnostic Approaches",
                                        "Treatment Methods",
                                        "Clinical Case Studies",
                                        "Review Questions"
                                    ].map((chapter, index) => (
                                        <button
                                            key={index}
                                            onClick={() => setSelectedChapter(chapter)}
                                            className={`w-full text-left px-4 py-3 border-b border-gray-50 last:border-b-0 hover:bg-gray-50 transition-colors flex items-center justify-between ${selectedChapter === chapter ? 'bg-gray-100' : ''
                                                }`}
                                        >
                                            <span className="text-gray-700">
                                                <span className="text-gray-400 mr-2">{index + 1}.</span>
                                                {chapter}
                                            </span>
                                            {selectedChapter === chapter && (
                                                <span className="text-xs bg-gray-800 text-white px-2 py-1 rounded">Selected</span>
                                            )}
                                        </button>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BookDetailView;
