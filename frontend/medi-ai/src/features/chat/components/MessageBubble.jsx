import React from 'react';

/**
 * MessageBubble Component
 * Displays individual chat messages with user/AI styling
 * @param {string} message - The message text
 * @param {boolean} isUser - Whether the message is from the user
 * @param {boolean} isTyping - Whether this is a typing indicator
 * @param {string} timestamp - Optional timestamp
 */
const MessageBubble = ({ message, isUser, isTyping = false, timestamp }) => {
    /**
     * Format timestamp to readable time
     * @returns {string} Formatted time
     */
    const formatTime = () => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div
            className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-slide-in`}
        >
            {/* AI Avatar */}
            {!isUser && !isTyping && (
                <div className="flex-shrink-0 mr-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-pink-600 rounded-full flex items-center justify-center shadow-soft">
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
                                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                            />
                        </svg>
                    </div>
                </div>
            )}

            {/* Typing Indicator Avatar */}
            {isTyping && (
                <div className="flex-shrink-0 mr-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-pink-600 rounded-full flex items-center justify-center shadow-soft">
                        <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                    </div>
                </div>
            )}

            {/* Message Content */}
            <div className={`max-w-[75%] ${isUser ? 'order-1' : 'order-2'}`}>
                {isTyping ? (
                    <div className="message-bubble-ai">
                        <div className="flex items-center space-x-1 py-2 px-3">
                            <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                    </div>
                ) : (
                    <>
                        <div className={isUser ? 'message-bubble-user' : 'message-bubble-ai'}>
                            <p className="whitespace-pre-wrap text-sm sm:text-base leading-relaxed">
                                {message}
                            </p>
                        </div>
                        {timestamp && (
                            <p className={`text-xs text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
                                {formatTime()}
                            </p>
                        )}
                    </>
                )}
            </div>

            {/* User Avatar */}
            {isUser && (
                <div className="flex-shrink-0 ml-3 order-2">
                    <div className="w-10 h-10 bg-gradient-to-br from-pink-300 to-pink-500 rounded-full flex items-center justify-center shadow-soft">
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
                                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                            />
                        </svg>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MessageBubble;
