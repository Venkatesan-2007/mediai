import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../shared/contexts/AuthContext';
import { sendMessage, getUploadedBooks } from '../../../shared/services/authService';
import '../../../shared/styles/Chat.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/* ── helpers ── */
const formatTime = (ts) =>
  new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

const WELCOME = {
  id: 0,
  text: '👋 Hello! I\'m your **Medical AI Assistant** powered by SambaNova.\n\nUpload PDFs in the Book List section and ask me anything about your medical documents — I\'ll retrieve the most relevant information and answer accurately.',
  sender: 'bot',
  timestamp: new Date(),
  sources: [],
};

/* ── sub-components ── */
const TypingDots = () => (
  <div className="typing-indicator">
    <span /><span /><span />
  </div>
);

const BotAvatar = () => (
  <div className="avatar bot-avatar">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" />
    </svg>
  </div>
);

const UserAvatar = () => (
  <div className="avatar user-avatar">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  </div>
);

const MessageBubble = ({ msg }) => {
  const isUser = msg.sender === 'user';
  const isError = msg.isError;

  const formatText = (text) =>
    text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>');

  return (
    <div className={`message-row ${isUser ? 'user-row' : 'bot-row'}`}>
      {!isUser && <BotAvatar />}
      <div className={`bubble ${isUser ? 'user-bubble' : 'bot-bubble'} ${isError ? 'error-bubble' : ''}`}>
        <p dangerouslySetInnerHTML={{ __html: formatText(msg.text) }} />
        {msg.sources && msg.sources.length > 0 && (
          <div className="sources-list">
            <span className="sources-label">📄 Sources:</span>
            {msg.sources.map((src, i) => (
              <span key={i} className="source-tag">{src}</span>
            ))}
          </div>
        )}
        <span className="bubble-time">{formatTime(msg.timestamp)}</span>
      </div>
      {isUser && <UserAvatar />}
    </div>
  );
};

/* ── main component ── */
const Chat = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadedPDFs, setUploadedPDFs] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [statusMsg, setStatusMsg] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => { loadUploadedPDFs(); loadChatHistory(); }, []); // eslint-disable-line
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  const loadUploadedPDFs = async () => {
    try {
      const res = await getUploadedBooks();
      setUploadedPDFs(res.books || []);
    } catch { /* silent */ }
  };

  const loadChatHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/api/chat-history`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
      });
      if (res.ok) {
        const data = await res.json();
        setChatHistory(data.history || []);
      }
    } catch { /* silent */ }
  };

  const startNewChat = () => {
    setMessages([WELCOME]);
    setCurrentChatId(null);
  };

  const loadChat = (chat) => {
    setMessages(chat.messages || [WELCOME]);
    setCurrentChatId(chat.id);
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { id: Date.now(), text, sender: 'user', timestamp: new Date() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput('');
    setLoading(true);
    setStatusMsg('SambaNova AI is thinking...');

    try {
      const res = await sendMessage(text, 'rag');
      const botMsg = {
        id: Date.now() + 1,
        text: res.answer || 'Sorry, I could not generate a response.',
        sender: 'bot',
        timestamp: new Date(),
        sources: res.sources || [],
      };
      const final = [...updated, botMsg];
      setMessages(final);
      saveChatMessage(userMsg, botMsg);
    } catch (err) {
      const errMsg = {
        id: Date.now() + 1,
        text: `⚠️ ${err.message || 'Connection error. Please check the backend is running.'}`,
        sender: 'bot',
        isError: true,
        timestamp: new Date(),
      };
      setMessages([...updated, errMsg]);
    } finally {
      setLoading(false);
      setStatusMsg('');
    }
  };

  const saveChatMessage = async (userMsg, botMsg) => {
    try {
      await fetch(`${API_URL}/api/chat-feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          user_message: userMsg.text,
          bot_response: botMsg.text,
          model_used: 'sambanova-rag',
          chat_id: currentChatId,
        }),
      });
      loadChatHistory();
    } catch { /* silent */ }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const autoResize = (e) => {
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px';
  };

  return (
    <div className="fullscreen-chat">

      {/* ── Sidebar ── */}
      <aside className={`chat-sidebar ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <div className="sidebar-brand">
          <div className="brand-logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <span className="brand-text">Medi AI</span>
          <button className="sidebar-collapse-btn" onClick={() => setSidebarOpen(false)} title="Collapse">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>

        <button className="new-chat-btn" onClick={startNewChat}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Chat
        </button>

        <div className="sidebar-section-title">Recent Chats</div>
        <div className="chat-history-list">
          {chatHistory.length === 0 ? (
            <p className="no-history">No chat history yet</p>
          ) : (
            chatHistory.map((chat) => (
              <button
                key={chat.id}
                className={`history-item ${currentChatId === chat.id ? 'history-item-active' : ''}`}
                onClick={() => loadChat(chat)}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span>{chat.title || `Chat ${chat.id}`}</span>
              </button>
            ))
          )}
        </div>

        {/* Uploaded PDFs */}
        {uploadedPDFs.length > 0 && (
          <>
            <div className="sidebar-section-title">Loaded Documents</div>
            <div className="docs-list">
              {uploadedPDFs.map((pdf) => (
                <div key={pdf.id} className="doc-item">
                  <span className="doc-icon">📄</span>
                  <span className="doc-name">{pdf.title || pdf.filename}</span>
                </div>
              ))}
            </div>
          </>
        )}

        {/* User + Logout */}
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar-sm">{(user?.username || 'U')[0].toUpperCase()}</div>
            <span className="user-name">{user?.username || 'User'}</span>
          </div>
          <button className="logout-btn" onClick={logout} title="Logout">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </aside>

      {/* ── Main Area ── */}
      <main className="chat-main-area">

        {/* Top bar */}
        <header className="chat-topbar">
          {!sidebarOpen && (
            <button className="open-sidebar-btn" onClick={() => setSidebarOpen(true)} title="Open sidebar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          )}
          <button className="back-btn" onClick={() => navigate('/dashboard')} title="Back to Dashboard">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="topbar-title">
            <div className="topbar-status-dot" />
            <h1>Medical RAG Chatbot</h1>
          </div>
          <div className="topbar-badge">
            <span className="model-badge">⚡ SambaNova · Llama 3.3-70B</span>
          </div>
        </header>

        {/* Messages */}
        <div className="messages-area">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}
          {loading && (
            <div className="message-row bot-row">
              <BotAvatar />
              <div className="bubble bot-bubble">
                <TypingDots />
                <span className="thinking-text">{statusMsg}</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => { setInput(e.target.value); autoResize(e); }}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your medical documents... (Enter to send, Shift+Enter for new line)"
              rows={1}
              disabled={loading}
              className="chat-textarea"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="send-btn"
              title="Send"
            >
              {loading ? (
                <svg className="spin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </div>
          <p className="disclaimer">⚠️ AI-generated information only. Always consult a qualified healthcare professional.</p>
        </div>
      </main>
    </div>
  );
};

export default Chat;
