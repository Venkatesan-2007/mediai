import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../shared/contexts/AuthContext';
import '../../../shared/styles/Login.css';

const Login = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [isLogin, setIsLogin] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // Form state
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });

    // Password strength
    const [passwordStrength, setPasswordStrength] = useState({
        score: 0,
        feedback: []
    });

    /**
     * Calculate password strength
     */
    const calculatePasswordStrength = (password) => {
        let score = 0;
        const feedback = [];

        if (password.length >= 8) {
            score += 25;
        } else {
            feedback.push('At least 8 characters');
        }

        if (/[a-z]/.test(password)) {
            score += 25;
        } else {
            feedback.push('Lowercase letter');
        }

        if (/[A-Z]/.test(password)) {
            score += 25;
        } else {
            feedback.push('Uppercase letter');
        }

        if (/[0-9]/.test(password)) {
            score += 15;
        } else {
            feedback.push('Number');
        }

        if (/[^A-Za-z0-9]/.test(password)) {
            score += 10;
        } else {
            feedback.push('Special character');
        }

        return { score, feedback };
    };

    /**
     * Handle input changes
     * @param {object} e - Event object
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
        setError('');

        // Update password strength for registration
        if (name === 'password' && !isLogin) {
            setPasswordStrength(calculatePasswordStrength(value));
        }
    };

    /**
     * Handle form submission
     * @param {object} e - Event object
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            // Validate password strength for registration
            if (!isLogin) {
                if (passwordStrength.score < 75) {
                    setError('Password is too weak. Please create a stronger password.');
                    setIsLoading(false);
                    return;
                }
            }

            const endpoint = isLogin ? '/auth/login' : '/auth/register';
            const response = await fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: formData.username,
                    password: formData.password,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                setError(data.detail || 'Authentication failed');
                return;
            }

            // Use auth context to save token and user
            login(data.access_token, data.user);
            
            // Redirect to dashboard
            navigate('/dashboard');
        } catch (err) {
            setError(err.message || 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Toggle between login and register
     */
    const toggleMode = () => {
        setIsLogin(!isLogin);
        setError('');
        setFormData({ username: '', password: '' });
        setPasswordStrength({ score: 0, feedback: [] });
    };

    /**
     * Get password strength class for CSS
     */
    const getStrengthClass = () => {
        if (passwordStrength.score < 25) return 'weak';
        if (passwordStrength.score < 50) return 'fair';
        if (passwordStrength.score < 75) return 'good';
        return 'strong';
    };

    /**
     * Get password strength text
     */
    const getStrengthText = () => {
        if (passwordStrength.score < 25) return 'Weak';
        if (passwordStrength.score < 50) return 'Fair';
        if (passwordStrength.score < 75) return 'Good';
        return 'Strong';
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h1>Medi AI</h1>
                <p className="subtitle">Medical PDF Analysis & Q&A</p>
                
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            placeholder="Enter username"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Enter password"
                            required
                        />
                        {!isLogin && formData.password && (
                            <div className="password-strength">
                                <div className="strength-bar">
                                    <div 
                                        className={`strength-fill ${getStrengthClass()}`}
                                        style={{ width: `${passwordStrength.score}%` }}
                                    ></div>
                                </div>
                                <div className="strength-text">
                                    <span>Password Strength: {getStrengthText()}</span>
                                </div>
                                {passwordStrength.feedback.length > 0 && (
                                    <div className="strength-feedback">
                                        <p>To improve:</p>
                                        <ul>
                                            {passwordStrength.feedback.map((item, index) => (
                                                <li key={index}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="submit-btn"
                    >
                        {isLoading ? 'Loading...' : (isLogin ? 'Login' : 'Register')}
                    </button>
                </form>

                <div className="toggle-mode">
                    <p>
                        {isLogin ? "Don't have an account? " : 'Already have an account? '}
                        <button
                            type="button"
                            onClick={toggleMode}
                            className="toggle-btn"
                        >
                            {isLogin ? 'Register' : 'Login'}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
