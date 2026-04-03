import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

/**
 * ChatBox Component
 * Main chat interface with message display and input
 * @param {Array} messages - Array of message objects
 * @param {function} onSendMessage - Callback to send message
 * @param {boolean} isTyping - Whether AI is typing
 */
const ChatBox = ({ messages, onSendMessage, isTyping }) => {
    const [inputValue, setInputValue] = useState('');
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    /**
     * Auto-scroll to bottom when new messages arrive
     */
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    /**
     * Handle input change
     * @param {object} e - Event object
     */
    const handleInputChange = (e) => {
        setInputValue(e.target.value);
    };

    /**
     * Handle form submission
     * @param {object} e - Event object
     */
    const handleSubmit = (e) => {
        e.preventDefault();
        if (inputValue.trim()) {
            onSendMessage(inputValue.trim());
            setInputValue('');
        }
    };

    /**
     * Handle Enter key press
     * @param {object} e - Event object
     */
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <div className="flex flex-col h-full bg-white/50 backdrop-blur-sm rounded-2xl shadow-card border border-pink-100 overflow-hidden">
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-pink-500 to-pink-600 p-4 shadow-soft">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <div>
                        <h2 className="text-white font-semibold text-lg">Medi AI Assistant</h2>
                        <div className="flex items-center space-x-1">
                            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                            <span className="text-white/80 text-sm">Online</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto p-4 scrollbar-pink space-y-2">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center p-8">
                        <div className="w-20 h-20 bg-gradient-to-br from-pink-100 to-pink-200 rounded-full flex items-center justify-center mb-4 animate-float">
                            <svg className="w-10 h-10 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-700 mb-2">Welcome to Medi AI!</h3>
                        <p className="text-gray-500 max-w-sm">
                            Ask me any health-related questions and I'll provide helpful information.
                            Remember, I'm not a substitute for professional medical advice.
                        </p>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <MessageBubble
                            key={index}
                            message={msg.text}
                            isUser={msg.isUser}
                            timestamp={msg.timestamp}
                        />
                    ))
                )}

                {/* Typing Indicator */}
                {isTyping && (
                    <MessageBubble
                        message=""
                        isUser={false}
                        isTyping={true}
                    />
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white/80 border-t border-pink-100">
                <form onSubmit={handleSubmit} className="flex items-center space-x-3">
                    <div className="flex-1 relative">
                        <input
                            ref={inputRef}
                            type="text"
                            value={inputValue}
                            onChange={handleInputChange}
                            onKeyPress={handleKeyPress}
                            placeholder="Type your health question..."
                            className="input-field pr-12"
                            disabled={isTyping}
                        />
                        <button
                            type="button"
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-pink-400 hover:text-pink-600 transition-colors"
                            title="Voice input (coming soon)"
                            disabled
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                            </svg>
                        </button>
                    </div>
                    <button
                        type="submit"
                        disabled={!inputValue.trim() || isTyping}
                        className={`btn-primary flex items-center justify-center w-14 h-12 px-0 ${!inputValue.trim() || isTyping ? 'opacity-50 cursor-not-allowed' : ''
                            }`}
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                    </button>
                </form>

                {/* Disclaimer */}
                <p className="text-xs text-gray-400 text-center mt-2">
                    ⚠️ This is an AI assistant for informational purposes only. Always consult a healthcare professional for medical advice.
                </p>
            </div>
        </div>
    );
};

export default ChatBox;
