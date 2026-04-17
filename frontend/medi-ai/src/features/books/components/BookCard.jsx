import React from 'react';

/**
 * BookCard Component
 * Displays a medical textbook in a card format with cover, details, and action buttons
 * @param {Object} book - Book object containing all book details
 * @param {Function} onOpen - Handler for opening book details
 * @param {Function} onAskFromBook - Handler for asking questions from the book
 */
const BookCard = ({ book, onOpen, onAskFromBook }) => {
    return (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
            {/* Book Cover */}
            <div className="relative h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                {book.coverImage ? (
                    <img
                        src={book.coverImage}
                        alt={book.title}
                        className="w-full h-full object-cover"
                    />
                ) : (
                    <div className="text-center p-4">
                        <div className="w-20 h-24 bg-gray-300 rounded-lg mx-auto mb-2 flex items-center justify-center">
                            <svg className="w-10 h-10 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                        </div>
                    </div>
                )}
                {/* Subject Badge */}
                <span className="absolute top-3 right-3 bg-gray-800/80 text-white text-xs px-2 py-1 rounded-full">
                    {book.subject}
                </span>
            </div>

            {/* Book Details */}
            <div className="p-4">
                <h3 className="font-semibold text-gray-800 text-lg mb-1 line-clamp-2">
                    {book.title}
                </h3>
                <p className="text-gray-500 text-sm mb-2">{book.author}</p>

                <div className="flex items-center justify-between text-xs text-gray-400 mb-4">
                    <span>📘 {book.edition}</span>
                    <span>📅 {book.year}</span>
                    <span className={`px-2 py-0.5 rounded ${book.type === 'Core' ? 'bg-blue-100 text-blue-700' : 'bg-pink-100 text-pink-700'}`}>
                        {book.type}
                    </span>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                    <button
                        onClick={() => onOpen(book)}
                        className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors text-sm"
                    >
                        Open
                    </button>
                    <button
                        onClick={() => onAskFromBook(book)}
                        className="flex-1 px-4 py-2 bg-gray-800 text-white rounded-xl font-medium hover:bg-gray-900 transition-colors text-sm"
                    >
                        Ask from this Book
                    </button>
                </div>
            </div>
        </div>
    );
};

export default BookCard;
