import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      await axios.post(`${API}/auth/forgot-password`, { email });
      setSuccess(true);
      
      // Redireciona para página de reset após 2 segundos
      setTimeout(() => {
        navigate('/reset-password', { state: { email } });
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao processar solicitação');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-form-section">
          <div className="auth-form-wrapper">
            <div className="logo-section">
              <img src={`${process.env.PUBLIC_URL}/images/logo.png`} alt="TAXXAT" className="auth-logo" />
            </div>

            <h1 className="auth-title">Esqueceu sua senha?</h1>
            <p className="auth-subtitle">Digite seu e-mail para receber o código de redefinição.</p>

            {error && (
              <div className="error-message" data-testid="error-message">
                {error}
              </div>
            )}

            {success && (
              <div className="success-message" data-testid="success-message">
                ✅ Código enviado! Verifique seu e-mail.
              </div>
            )}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="email">E-mail</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com"
                  required
                  data-testid="email-input"
                />
              </div>

              <button 
                type="submit" 
                className="btn btn-primary btn-full" 
                disabled={loading}
                data-testid="submit-button"
              >
                {loading ? 'Enviando...' : 'Enviar Código'}
              </button>
            </form>

            <div className="auth-links">
              <button onClick={() => navigate('/login')} className="link-button" data-testid="back-to-login">
                ← Voltar para Login
              </button>
            </div>
          </div>
        </div>

        <div className="auth-banner-section">
          <div className="banner-overlay">
            <div className="banner-content">
              <h2>🔐 Recuperação de Senha</h2>
              <ul className="banner-list">
                <li>📧 Receba um código por e-mail</li>
                <li>⏱️ Código válido por 15 minutos</li>
                <li>🔒 Processo 100% seguro</li>
                <li>✅ Redefina sua senha rapidamente</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
