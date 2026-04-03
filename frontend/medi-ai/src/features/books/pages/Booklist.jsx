import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../../shared/components/Navbar';
import SearchBar from '../components/SearchBar';
import { useAuth } from '../../../shared/contexts/AuthContext';
import { uploadPDF, getUploadedBooks } from '../../../shared/services/authService';

/**
 * Booklist Page Component
 * Simplified version - Shows only uploaded books for chat and AI usage
 */
const Booklist = () => {
    const navigate = useNavigate();
    const { logout } = useAuth();
    const [searchTerm, setSearchTerm] = useState('');
    const [uploadedBooks, setUploadedBooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [uploadError, setUploadError] = useState('');
    const [uploadSuccess, setUploadSuccess] = useState('');
    const fileInputRef = React.useRef(null);

    // Load uploaded books on mount
    useEffect(() => {
        const loadBooks = async () => {
            try {
                const booksData = await getUploadedBooks();
                
                if (booksData.books && booksData.books.length > 0) {
                    const convertedBooks = booksData.books.map(book => ({
                        id: book.id,
                        title: book.title || book.filename?.replace('.pdf', '') || 'Untitled',
                        author: 'PDF Upload',
                        edition: "PDF",
                        year: "2026",
                        subject: "Medical",
                        type: "PDF",
                        description: `${book.chunks_count} chunks extracted for AI analysis`,
                        isUploadedPDF: true,
                        chunks_count: book.chunks_count
                    }));
                    setUploadedBooks(convertedBooks);
                }
            } catch (error) {
                console.error('Error loading books:', error);
            } finally {
                setLoading(false);
            }
        };

        loadBooks();
    }, []);

    /**
     * Handle PDF file upload
     */
    const handlePDFUpload = async (file) => {
        setUploadError('');
        setUploadSuccess('');
        
        // Validate PDF
        if (!file.name.endsWith('.pdf')) {
            setUploadError('Please upload a PDF file only');
            return;
        }
        
        if (file.size > 50 * 1024 * 1024) {
            setUploadError('File too large. Maximum 50MB allowed.');
            return;
        }

        setUploading(true);

        try {
            await uploadPDF(file);
            
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }

            // Reload uploaded books
            const booksData = await getUploadedBooks();
            
            if (booksData.books) {
                const convertedBooks = booksData.books.map(book => ({
                    id: book.id,
                    title: book.title || book.filename?.replace('.pdf', '') || 'Untitled',
                    author: 'PDF Upload',
                    edition: "PDF",
                    year: "2026",
                    subject: "Medical",
                    type: "PDF",
                    description: `${book.chunks_count} chunks extracted for AI analysis`,
                    isUploadedPDF: true,
                    chunks_count: book.chunks_count
                }));
                setUploadedBooks(convertedBooks);
                setUploadSuccess(`✓ "${file.name}" uploaded successfully`);
                setTimeout(() => setUploadSuccess(''), 3000);
            }
        } catch (error) {
            setUploadError(error.message || 'Upload failed');
            console.error('Upload error:', error);
        } finally {
            setUploading(false);
        }
    };

    const handleFileSelect = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            handlePDFUpload(file);
        }
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const file = e.dataTransfer.files?.[0];
        if (file && file.type === 'application/pdf') {
            handlePDFUpload(file);
        } else {
            setUploadError('Please drop a PDF file');
        }
    };

    // Filter uploaded books based on search
    const filteredBooks = uploadedBooks.filter(book => {
        const matchesSearch = searchTerm === '' ||
            book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            book.author.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSearch;
    });

    /**
     * Handle using book in chat
     */
    const handleUseInChat = (book) => {
        const context = `Using the uploaded book: "${book.title}" (${book.chunks_count} chunks). Please answer based on this book's content.`;
        sessionStorage.setItem('bookContext', context);
        sessionStorage.setItem('selectedBook', JSON.stringify(book));
        navigate('/chat');
    };

    /**
     * Handle using book for AI questions
     */
    const handleUseForAI = (book) => {
        sessionStorage.setItem('selectedBookId', book.id);
        sessionStorage.setItem('selectedBookTitle', book.title);
        navigate('/chat');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-pink-50 to-blue-50 flex flex-col">
            <Navbar onLogout={logout} />

            <main className="flex-1 container mx-auto px-4 py-8 max-w-5xl">
                {/* Page Header */}
                <div className="mb-8">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="flex items-center space-x-2 px-4 py-2 bg-white text-gray-600 rounded-xl hover:bg-gray-100 transition-colors shadow-sm mb-4"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        <span>Back</span>
                    </button>
                    <div>
                        <h1 className="text-4xl font-bold text-gray-800">My Books</h1>
                        <p className="text-gray-500 mt-2">Upload medical documents for AI analysis and chat</p>
                    </div>
                </div>

                {/* PDF Upload Section */}
                <div 
                    className={`mb-8 border-2 border-dashed rounded-2xl p-10 text-center transition-all ${uploading ? 'border-pink-300 bg-pink-50/50' : 'border-pink-200 hover:border-pink-400 bg-white hover:bg-pink-50/30'} cursor-pointer shadow-sm`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => !uploading && fileInputRef.current?.click()}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf"
                        onChange={handleFileSelect}
                        disabled={uploading}
                        className="hidden"
                    />
                    
                    {uploading ? (
                        <div>
                            <div className="w-10 h-10 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin mx-auto mb-3"></div>
                            <p className="text-gray-600 font-semibold">Processing PDF...</p>
                            <p className="text-gray-500 text-sm mt-1">This may take a moment</p>
                        </div>
                    ) : (
                        <div>
                            <svg className="w-12 h-12 text-pink-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            <p className="text-gray-700 font-bold text-lg">Upload Medical Books</p>
                            <p className="text-gray-500 mt-1">Drag & drop PDF files or click to browse</p>
                            <p className="text-gray-400 text-sm mt-2">Max 50MB per file  Supports medical textbooks, research papers, notes</p>
                        </div>
                    )}
                </div>

                {/* Error Message */}
                {uploadError && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-start">
                        <svg className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                            <p className="font-semibold">Upload Error</p>
                            <p className="text-sm">{uploadError}</p>
                        </div>
                    </div>
                )}

                {/* Success Message */}
                {uploadSuccess && (
                    <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl text-green-700 flex items-center">
                        <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {uploadSuccess}
                    </div>
                )}

                {/* Search Bar */}
                {uploadedBooks.length > 0 && (
                    <div className="mb-6">
                        <SearchBar
                            searchTerm={searchTerm}
                            onSearch={setSearchTerm}
                        />
                    </div>
                )}

                {/* Books Count */}
                {uploadedBooks.length > 0 && (
                    <div className="mb-4 text-gray-600">
                        <p className="font-medium">{filteredBooks.length} of {uploadedBooks.length} books</p>
                    </div>
                )}

                {/* Books Grid or Empty State */}
                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="text-center">
                            <div className="w-12 h-12 border-4 border-gray-200 border-t-pink-600 rounded-full animate-spin mx-auto mb-4"></div>
                            <p className="text-gray-500">Loading your books...</p>
                        </div>
                    </div>
                ) : uploadedBooks.length === 0 ? (
                    <div className="text-center py-16 bg-white rounded-2xl border border-pink-100 shadow-sm">
                        <svg className="w-20 h-20 text-pink-200 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                        <p className="text-gray-500 text-lg font-medium">No books uploaded yet</p>
                        <p className="text-gray-400 mt-1">Upload a PDF to get started with AI analysis and chat</p>
                    </div>
                ) : filteredBooks.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-2xl border border-pink-100">
                        <p className="text-gray-500">No books match your search</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredBooks.map((book) => (
                            <div key={book.id} className="bg-white rounded-2xl shadow-sm border border-pink-100 overflow-hidden hover:shadow-md transition-shadow">
                                {/* Book Icon */}
                                <div className="h-32 bg-gradient-to-br from-pink-100 to-pink-50 flex items-center justify-center">
                                    <svg className="w-16 h-16 text-pink-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                </div>

                                {/* Book Info */}
                                <div className="p-5">
                                    <h3 className="font-bold text-gray-800 line-clamp-2 mb-2">{book.title}</h3>
                                    <p className="text-sm text-gray-500 mb-3">{book.chunks_count} chunks  PDF</p>
                                    
                                    {/* Action Buttons */}
                                    <div className="space-y-2">
                                        <button
                                            onClick={() => handleUseInChat(book)}
                                            className="w-full px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors text-sm font-medium flex items-center justify-center"
                                        >
                                            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.030 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.030-8 9-8s9 3.582 9 8z" />
                                            </svg>
                                            Use in Chat
                                        </button>
                                        <button
                                            onClick={() => handleUseForAI(book)}
                                            className="w-full px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors text-sm font-medium flex items-center justify-center"
                                        >
                                            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                            </svg>
                                            AI Questions
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="py-6 text-center text-gray-400 text-sm bg-white border-t border-gray-100 mt-8">
                <p> 2026 Medi AI - Your Health Assistant</p>
            </footer>
        </div>
    );
};

export default Booklist;
