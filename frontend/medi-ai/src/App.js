import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './shared/contexts/AuthContext';
import Login from './features/auth/pages/Login';
import Dashboard from './features/dashboard/pages/Dashboard';
import Chat from './features/chat/pages/Chat';
import SignatureAnalysis from './features/signatureAnalysis/pages/SignatureAnalysis';
import QuestionBuilder from './features/questionBuilder/pages/QuestionBuilder';
import Booklist from './features/books/pages/Booklist';

/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Loading...</div>;
  }

  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

/**
 * Main App Content Component
 * Sets up routing and protected routes
 */
function AppContent() {
  return (
    <Routes>
      {/* Public Routes - Login */}
      <Route
        path="/login"
        element={<Login />}
      />

      {/* Protected Routes - Dashboard */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* Protected Routes - Chat */}
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <Chat />
          </ProtectedRoute>
        }
      />

      {/* Protected Routes - Signature Analysis */}
      <Route
        path="/signature-analysis"
        element={
          <ProtectedRoute>
            <SignatureAnalysis />
          </ProtectedRoute>
        }
      />

      {/* Protected Routes - Question Builder */}
      <Route
        path="/questions"
        element={
          <ProtectedRoute>
            <QuestionBuilder />
          </ProtectedRoute>
        }
      />

      {/* Protected Routes - Booklist */}
      <Route
        path="/booklist"
        element={
          <ProtectedRoute>
            <Booklist />
          </ProtectedRoute>
        }
      />

      {/* Default redirect */}
      <Route
        path="/"
        element={<Navigate to="/login" replace />}
      />

      {/* Catch all - redirect to login */}
      <Route
        path="*"
        element={<Navigate to="/login" replace />}
      />
    </Routes>
  );
}

/**
 * Main App Component
 * Wraps with AuthProvider for global auth state
 */
function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
