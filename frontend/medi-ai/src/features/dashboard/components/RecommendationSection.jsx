import React from 'react';

/**
 * RecommendationSection Component
 * Displays recommendations including high-yield topics, exam recommended chapters, and most accessed books
 * @param {Function} onBookClick - Handler for clicking on a recommended book
 */
const RecommendationSection = ({ onBookClick }) => {
    const highYieldTopics = [
        { id: 1, topic: "Cardiovascular System", importance: "High" },
        { id: 2, topic: "Respiratory Diseases", importance: "High" },
        { id: 3, topic: "CNS Pharmacology", importance: "High" },
        { id: 4, topic: "Renal Physiology", importance: "Medium" },
        { id: 5, topic: "GI Pathology", importance: "Medium" }
    ];

    const examRecommendedChapters = [
        { id: 1, chapter: "Heart Anatomy", book: "Gray's Anatomy", examWeight: "90%" },
        { id: 2, chapter: "ECG Interpretation", book: "Clinical Cardiology", examWeight: "95%" },
        { id: 3, chapter: "Respiratory Failure", book: "Harrison's Principles", examWeight: "88%" },
        { id: 4, chapter: "Diabetes Mellitus", book: "Williams Textbook", examWeight: "92%" }
    ];

    const mostAccessedBooks = [
        { id: 1, title: "Gray's Anatomy", author: "Henry Gray", views: 2453 },
        { id: 2, title: "Harrison's Principles of Internal Medicine", author: "Dennis Kasper", views: 2102 },
        { id: 3, title: "Robbins Pathologic Basis of Disease", author: "Vinay Kumar", views: 1890 },
        { id: 4, title: "Ganong's Review of Medical Physiology", author: "Kim Barrett", views: 1654 }
    ];

    return (
        <div className="space-y-6">
            {/* High Yield Topics */}
            <div className="bg-white rounded-xl border border-gray-100 p-4">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    High-Yield Topics
                </h3>
                <div className="flex flex-wrap gap-2">
                    {highYieldTopics.map((item) => (
                        <span
                            key={item.id}
                            className="px-3 py-1.5 bg-green-50 text-green-700 rounded-lg text-sm font-medium"
                        >
                            {item.topic}
                        </span>
                    ))}
                </div>
            </div>

            {/* Exam Recommended Chapters */}
            <div className="bg-white rounded-xl border border-gray-100 p-4">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    Exam Recommended Chapters
                </h3>
                <div className="space-y-2">
                    {examRecommendedChapters.map((item) => (
                        <div
                            key={item.id}
                            className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                        >
                            <div>
                                <span className="text-gray-800 font-medium text-sm">{item.chapter}</span>
                                <span className="text-gray-400 text-xs ml-2">• {item.book}</span>
                            </div>
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                                {item.examWeight}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Most Accessed Books */}
            <div className="bg-white rounded-xl border border-gray-100 p-4">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                    Most Accessed Books
                </h3>
                <div className="space-y-2">
                    {mostAccessedBooks.map((book, index) => (
                        <button
                            key={book.id}
                            onClick={() => onBookClick(book)}
                            className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg transition-colors text-left"
                        >
                            <div className="flex items-center space-x-3">
                                <span className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-medium">
                                    {index + 1}
                                </span>
                                <div>
                                    <span className="text-gray-800 font-medium text-sm block">{book.title}</span>
                                    <span className="text-gray-400 text-xs">{book.author}</span>
                                </div>
                            </div>
                            <span className="text-gray-400 text-xs">👁 {book.views}</span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default RecommendationSection;
