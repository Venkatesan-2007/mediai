import React, { useState, useEffect } from 'react';
import Navbar from '../../../shared/components/Navbar';
import MessageBubble from '../components/MessageBubble';
import { useAuth } from '../../../shared/contexts/AuthContext';
import { sendMessage, getUploadedBooks } from '../services/authService';
import '../../../shared/styles/Chat.css';

/**
 * Chat Page Component
 * AI chat interface with authenticated PDF context
 */
const Chat = () => {
  const { logout } = useAuth();
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hello! I can help you analyze medical documents. Upload PDFs in the Book List section and ask me questions about them.',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadedPDFs, setUploadedPDFs] = useState([]);
  const [selectedModel, setSelectedModel] = useState('rag');
  const [chatHistory, setChatHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);

  // Load uploaded PDFs and chat history on mount
  useEffect(() => {
    loadUploadedPDFs();
    loadChatHistory();
  }, []);

  const loadUploadedPDFs = async () => {
    try {
      const response = await getUploadedBooks();
      setUploadedPDFs(response.books || []);
    } catch (err) {
      console.error('Error loading PDFs:', err);
    }
  };

  const loadChatHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/chat-history', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setChatHistory(data.history || []);
      }
    } catch (err) {
      console.error('Error loading chat history:', err);
    }
  };

  const startNewChat = () => {
    setMessages([
      {
        id: 1,
        text: 'Hello! I can help you analyze medical documents. Upload PDFs in the Book List section and ask me questions about them.',
        sender: 'bot',
        timestamp: new Date(),
      },
    ]);
    setCurrentChatId(null);
  };

  const loadChat = (chatId) => {
    const chat = chatHistory.find(c => c.id === chatId);
    if (chat) {
      setMessages(chat.messages || []);
      setCurrentChatId(chatId);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await sendMessage(input, selectedModel);
      const botMessage = {
        id: messages.length + 2,
        text: response.answer,
        sender: 'bot',
        sources: response.sources,
        timestamp: new Date(),
      };
      const finalMessages = [...newMessages, botMessage];
      setMessages(finalMessages);

      // Save to backend
      await saveChatMessage(userMessage, botMessage);
    } catch (err) {
      const errorMessage = {
        id: messages.length + 2,
        text: `Error: ${err.message}`,
        sender: 'bot',
        timestamp: new Date(),
      };
      const finalMessages = [...newMessages, errorMessage];
      setMessages(finalMessages);
    } finally {
      setLoading(false);
    }
  };

  const saveChatMessage = async (userMessage, botMessage) => {
    try {
      await fetch('http://localhost:8000/api/chat-feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          user_message: userMessage.text,
          bot_response: botMessage.text,
          model_used: selectedModel,
          chat_id: currentChatId,
        }),
      });
      // Reload chat history after saving
      loadChatHistory();
    } catch (err) {
      console.error('Error saving chat message:', err);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-container">
      <Navbar onLogout={logout} />
      <div className="chat-main">
        {/* Chat History Sidebar */}
        <div className={`chat-sidebar ${showHistory ? 'open' : ''}`}>
          <div className="sidebar-header">
            <h3>Chat History</h3>
            <button onClick={() => setShowHistory(!showHistory)} className="sidebar-toggle">
              {showHistory ? '◁' : '▷'}
            </button>
          </div>
          <div className="sidebar-content">
            <button onClick={startNewChat} className="new-chat-btn">
              + New Chat
            </button>
            <div className="chat-list">
              {chatHistory.map((chat) => (
                <div
                  key={chat.id}
                  className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                  onClick={() => loadChat(chat.id)}
                >
                  <div className="chat-title">
                    {chat.title || `Chat ${chat.id}`}
                  </div>
                  <div className="chat-date">
                    {new Date(chat.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="chat-content">
          <div className="chat-header">
            <button onClick={() => setShowHistory(!showHistory)} className="history-toggle">
              {showHistory ? '◁ Hide History' : '▷ Show History'}
            </button>
            <h2>Medical AI Chat</h2>
          </div>
          <div className="chat-messages">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg.text}
                isUser={msg.sender === 'user'}
                timestamp={msg.timestamp}
              />
            ))}
            {loading && (
              <div className="loading-indicator">
                <span></span><span></span><span></span>
              </div>
            )}
          </div>

          <div className="chat-input-area">
            <div className="model-selector">
              <label htmlFor="model-select">Chat Mode:</label>
              <select
                id="model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                disabled={loading}
              >
                <option value="rag">RAG Model (With Documents)</option>
                <option value="normal">Normal Model (General Knowledge)</option>
              </select>
            </div>
            <div>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your documents..."
                rows="3"
              />
              <button onClick={handleSendMessage} disabled={loading || !input.trim()}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>

          {uploadedPDFs.length > 0 && (
            <div className="documents-info">
              <p>📚 Documents ({uploadedPDFs.length}):</p>
              <ul>
                {uploadedPDFs.map((pdf) => (
                  <li key={pdf.id}>{pdf.title}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chat;
