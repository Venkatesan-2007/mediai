import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../../shared/components/Navbar';
import { useAuth } from '../../../shared/contexts/AuthContext';

/**
 * QuestionBuilder Page Component
 * AI-powered question generator for study topics
 * Can use selected book context if available
 */
const QuestionBuilder = () => {
    const navigate = useNavigate();
    const { logout } = useAuth();
    const [topic, setTopic] = useState('');
    const [selectedBook, setSelectedBook] = useState(null);
    const [booksList, setBooksList] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [filteredBooks, setFilteredBooks] = useState([]);
    const [showBookDropdown, setShowBookDropdown] = useState(false);
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [booksLoading, setBooksLoading] = useState(true);
    const [error, setError] = useState('');
    const [booksError, setBooksError] = useState('');
    const [difficulty, setDifficulty] = useState('mixed');
    const [numQuestions, setNumQuestions] = useState(5);

    // Fetch user's uploaded books on mount
    useEffect(() => {
        const fetchBooks = async () => {
            try {
                setBooksLoading(true);
                setBooksError('');
                const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
                const token = localStorage.getItem('auth_token');

                const response = await fetch(`${API_URL}/api/uploaded-pdfs`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token && { 'Authorization': `Bearer ${token}` }),
                    },
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch books');
                }

                const data = await response.json();
                const books = data.pdfs || [];
                setBooksList(books);
                setFilteredBooks(books);
            } catch (err) {
                setBooksError(err.message || 'Failed to load books');
                console.error('Books fetch error:', err);
            } finally {
                setBooksLoading(false);
            }
        };

        fetchBooks();

        // Check for selected book from sessionStorage on mount
        const bookData = sessionStorage.getItem('selectedBook');
        if (bookData) {
            try {
                const book = JSON.parse(bookData);
                setSelectedBook(book);
                // Clear from sessionStorage after reading
                sessionStorage.removeItem('selectedBook');
            } catch (e) {
                console.error('Error loading selected book:', e);
            }
        }
    }, []);

    // Filter books based on search query
    useEffect(() => {
        if (searchQuery.trim() === '') {
            setFilteredBooks(booksList);
        } else {
            const query = searchQuery.toLowerCase();
            const filtered = booksList.filter(book =>
                book.title.toLowerCase().includes(query) ||
                book.filename.toLowerCase().includes(query)
            );
            setFilteredBooks(filtered);
        }
    }, [searchQuery, booksList]);

    /**
     * Handle back button click - navigate to dashboard
     */
    const handleBack = () => {
        navigate('/dashboard');
    };

    /**
     * Generate questions based on topic input and selected book
     * Book selection is mandatory
     */
    const handleGenerateQuestions = async () => {
        if (!selectedBook) {
            setError('Please select a book first');
            return;
        }

        if (!topic.trim()) {
            setError('Please enter a topic name');
            return;
        }

        setError('');
        setLoading(true);
        setQuestions([]);

        try {
            const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
            const token = localStorage.getItem('auth_token');
            
            const payload = {
                topic: topic.trim(),
                difficulty_level: difficulty,
                question_type: 'mixed',
                num_questions: numQuestions,
                from_book_content: true,
                book_id: selectedBook.id
            };

            const response = await fetch(`${API_URL}/api/generate-questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token && { 'Authorization': `Bearer ${token}` }),
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate questions');
            }

            const data = await response.json();
            setQuestions(data.questions || []);
        } catch (err) {
            setError(err.message || 'Failed to generate questions. Please try again.');
            console.error('Question generation error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleClearBook = () => {
        setSelectedBook(null);
        setSearchQuery('');
        setShowBookDropdown(false);
    };

    const handleSelectBook = (book) => {
        setSelectedBook(book);
        setSearchQuery('');
        setShowBookDropdown(false);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-pink-50 to-blue-50 flex flex-col">
            <Navbar onLogout={logout} />

            <main className="flex-1 container mx-auto px-4 py-8 max-w-4xl">
                {/* Page Header with Back Button */}
                <div className="flex items-center mb-8">
                    <button
                        onClick={handleBack}
                        className="flex items-center space-x-2 px-4 py-2 bg-white text-gray-600 rounded-xl hover:bg-gray-100 transition-colors shadow-sm mr-4"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        <span>Back</span>
                    </button>
                    <div>
                        <h1 className="text-4xl font-bold text-gray-800">AI Question Builder</h1>
                        <p className="text-gray-500 mt-2">Generate practice questions for any topic</p>
                    </div>
                </div>

                {/* Book Selection Section */}
                <div className="bg-white rounded-2xl shadow-sm border border-purple-100 p-6 mb-6">
                    <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                        <svg className="w-6 h-6 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                        Select Book <span className="text-red-500 ml-1">*</span>
                    </h2>

                    {booksError && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 mb-4">
                            <p className="font-medium">Unable to load books</p>
                            <p className="text-sm">{booksError}</p>
                            <button
                                onClick={() => navigate('/booklist')}
                                className="text-red-600 hover:text-red-700 font-medium text-sm mt-2 underline"
                            >
                                Go to Booklist to upload books
                            </button>
                        </div>
                    )}

                    {!booksError && booksList.length === 0 && !booksLoading && (
                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl text-yellow-700 mb-4">
                            <p className="font-medium">No books uploaded yet</p>
                            <p className="text-sm mb-2">You need to upload at least one book to generate questions from.</p>
                            <button
                                onClick={() => navigate('/booklist')}
                                className="text-yellow-600 hover:text-yellow-700 font-medium text-sm underline"
                            >
                                Go to Booklist to upload books
                            </button>
                        </div>
                    )}

                    {booksLoading ? (
                        <div className="flex items-center justify-center py-8">
                            <svg className="w-6 h-6 animate-spin text-purple-500" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span className="ml-2 text-gray-600">Loading books...</span>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {/* Search Bar */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Search Books</label>
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => {
                                        setSearchQuery(e.target.value);
                                        setShowBookDropdown(true);
                                    }}
                                    onFocus={() => setShowBookDropdown(true)}
                                    onClick={() => setShowBookDropdown(!showBookDropdown)}
                                    placeholder="Search by title or filename..."
                                    className="w-full px-4 py-3 border-2 border-purple-200 rounded-xl focus:border-purple-400 focus:outline-none transition-colors text-gray-700 placeholder-gray-400"
                                />
                            </div>

                            {/* Book Dropdown List */}
                            {showBookDropdown && filteredBooks.length > 0 && (
                                <div className="relative">
                                    <div className="absolute top-0 left-0 right-0 bg-white border-2 border-purple-200 rounded-xl shadow-lg max-h-64 overflow-y-auto z-20">
                                        {filteredBooks.map((book) => (
                                            <button
                                                key={book.id}
                                                onClick={() => handleSelectBook(book)}
                                                className="w-full text-left px-4 py-3 hover:bg-purple-50 border-b border-purple-100 last:border-b-0 transition-colors"
                                            >
                                                <div className="flex items-start justify-between">
                                                    <div className="flex-1">
                                                        <p className="font-medium text-gray-800">{book.title}</p>
                                                        <p className="text-xs text-gray-500 mt-1">
                                                            {book.chunks_count ? `${book.chunks_count} chunks` : 'PDF uploaded'}
                                                        </p>
                                                    </div>
                                                    {selectedBook?.id === book.id && (
                                                        <svg className="w-5 h-5 text-purple-600 flex-shrink-0 ml-2" fill="currentColor" viewBox="0 0 20 20">
                                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                        </svg>
                                                    )}
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* No results message */}
                            {showBookDropdown && filteredBooks.length === 0 && searchQuery.trim() !== '' && (
                                <div className="p-4 bg-gray-50 rounded-xl border border-gray-200 text-center">
                                    <p className="text-gray-600 text-sm">No books found matching "{searchQuery}"</p>
                                </div>
                            )}

                            {/* Selected Book Display */}
                            {selectedBook && (
                                <div className="p-4 bg-purple-50 border-2 border-purple-200 rounded-xl flex items-center justify-between">
                                    <div className="flex items-center space-x-3 flex-1">
                                        <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                        <div>
                                            <p className="text-sm text-purple-600 font-medium">Selected Book</p>
                                            <p className="text-lg font-semibold text-purple-900">{selectedBook.title}</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={handleClearBook}
                                        className="text-purple-600 hover:text-purple-700 font-medium text-sm rounded-lg hover:bg-purple-100 px-3 py-2 transition-colors"
                                    >
                                        Change
                                    </button>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Topic Input Section */}
                <div className="bg-white rounded-2xl shadow-sm border border-pink-100 p-6 mb-6">
                    <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                        <svg className="w-6 h-6 mr-2 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        Topic & Settings
                    </h2>

                    <div className="space-y-4">
                        {/* Topic Input */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Topic</label>
                            <input
                                type="text"
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="e.g., Cardiovascular System, Anatomy, Pharmacology..."
                                className="w-full px-4 py-3 border-2 border-pink-200 rounded-xl focus:border-pink-400 focus:outline-none transition-colors text-gray-700 placeholder-gray-400"
                            />
                        </div>

                        {/* Settings Row */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Difficulty Level */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                                <select
                                    value={difficulty}
                                    onChange={(e) => setDifficulty(e.target.value)}
                                    className="w-full px-4 py-3 border-2 border-pink-200 rounded-xl focus:border-pink-400 focus:outline-none transition-colors text-gray-700"
                                >
                                    <option value="mixed">Mixed</option>
                                    <option value="easy">Easy</option>
                                    <option value="medium">Medium</option>
                                    <option value="hard">Hard</option>
                                </select>
                            </div>

                            {/* Number of Questions */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
                                <select
                                    value={numQuestions}
                                    onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                                    className="w-full px-4 py-3 border-2 border-pink-200 rounded-xl focus:border-pink-400 focus:outline-none transition-colors text-gray-700"
                                >
                                    {[3, 5, 7, 10, 15, 20].map(n => (
                                        <option key={n} value={n}>{n} questions</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {/* Generate Button */}
                        <button
                            onClick={handleGenerateQuestions}
                            disabled={loading || !selectedBook}
                            title={!selectedBook ? "Please select a book first" : ""}
                            className={`w-full px-6 py-3 bg-gradient-to-r from-pink-500 to-pink-600 text-white font-semibold rounded-xl transition-all duration-300 shadow-sm flex items-center justify-center space-x-2 ${loading || !selectedBook ? 'opacity-60 cursor-not-allowed' : 'hover:from-pink-600 hover:to-pink-700 hover:scale-105'
                                }`}
                        >
                            {loading ? (
                                <>
                                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    <span>Generating...</span>
                                </>
                            ) : (
                                <>
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                    <span>{!selectedBook ? 'Select a book first' : 'Generate Questions'}</span>
                                </>
                            )}
                        </button>

                        {error && (
                            <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
                                <p className="font-medium">Error</p>
                                <p className="text-sm">{error}</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Generated Questions Section */}
                <div className="bg-white rounded-2xl shadow-sm border border-pink-100 p-6">
                    <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                        <svg className="w-6 h-6 mr-2 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Questions
                        {questions.length > 0 && (
                            <span className="ml-2 text-sm text-gray-400 font-normal">
                                ({questions.length} generated)
                            </span>
                        )}
                    </h2>

                    {questions.length === 0 && !loading ? (
                        <div className="text-center py-16">
                            <div className="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg className="w-8 h-8 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                </svg>
                            </div>
                            <p className="text-gray-500 text-lg">Enter a topic and click "Generate Questions" to get started</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {questions.map((q, index) => (
                                <div
                                    key={index}
                                    className="p-5 bg-gradient-to-br from-pink-50 to-purple-50 rounded-xl border border-pink-100 hover:shadow-md transition-shadow"
                                >
                                    {/* Question Header */}
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center space-x-2">
                                            <span className="text-pink-600 font-semibold text-xs bg-pink-100 px-3 py-1 rounded-full uppercase">
                                                {q.type.replace('_', ' ')}
                                            </span>
                                            <span className="text-purple-600 font-semibold text-xs bg-purple-100 px-3 py-1 rounded-full capitalize">
                                                {q.difficulty}
                                            </span>
                                        </div>
                                        <span className="text-gray-400 text-sm font-medium">Q{index + 1}</span>
                                    </div>

                                    {/* Question Text */}
                                    <p className="text-gray-800 font-medium text-base mb-4 leading-relaxed">{q.question}</p>

                                    {/* Multiple Choice Options */}
                                    {q.type === 'multiple_choice' && q.options && (
                                        <div className="space-y-2 ml-2 mb-4">
                                            {q.options.map((option, idx) => (
                                                <div
                                                    key={idx}
                                                    className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-pink-100"
                                                >
                                                    <span className="w-6 h-6 bg-pink-200 text-pink-700 rounded-full flex items-center justify-center text-xs font-bold">
                                                        {String.fromCharCode(65 + idx)}
                                                    </span>
                                                    <span className="text-gray-700 text-sm">{option}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Correct Answer & Explanation */}
                                    {q.correct_answer && (
                                        <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
                                            <p className="text-green-700 font-semibold text-sm mb-1">✓ Answer:</p>
                                            <p className="text-gray-700 text-sm mb-2">{q.correct_answer}</p>
                                            {q.explanation && (
                                                <p className="text-gray-600 text-sm italic">{q.explanation}</p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </main>

            {/* Footer */}
            <footer className="py-6 text-center text-gray-400 text-sm bg-white border-t border-gray-100 mt-8">
                <p>© 2026 Medi AI - Your Health Assistant</p>
            </footer>
        </div>
    );
};

export default QuestionBuilder;
