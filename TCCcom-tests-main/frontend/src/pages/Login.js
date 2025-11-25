import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    senha: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(
        `${API}/auth/login`,
        formData,
        { withCredentials: true }
      );

      // Save user to localStorage
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao fazer login');
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

            <h1 className="auth-title">Entrar na sua conta</h1>
            <p className="auth-subtitle">Bem-vindo de volta! Acesse seu assistente de IR.</p>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="email">E-mail</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="seu@email.com"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="senha">Senha</label>
                <input
                  type="password"
                  id="senha"
                  name="senha"
                  value={formData.senha}
                  onChange={handleChange}
                  placeholder="••••••••"
                  required
                />
              </div>

              <div className="forgot-password-link">
                <button 
                  type="button"
                  onClick={() => navigate('/forgot-password')} 
                  className="link-button"
                  data-testid="forgot-password-link"
                >
                  Esqueceu sua senha?
                </button>
              </div>

              <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? 'Entrando...' : 'Entrar'}
              </button>
            </form>

            <div className="auth-links">
              <p>
                Não tem uma conta?{' '}
                <button onClick={() => navigate('/register')} className="link-button">
                  Cadastre-se aqui
                </button>
              </p>
              <button onClick={() => navigate('/')} className="link-button">
                ← Voltar para início
              </button>
            </div>
          </div>
        </div>

        <div className="auth-banner-section">
          <div className="banner-overlay">
            <div className="banner-content">
              <h2>🚀 Simplifique sua declaração de IR</h2>
              <ul className="banner-list">
                <li>✅ Chatbot com IA disponível 24/7</li>
                <li>✅ Upload e análise de documentos</li>
                <li>✅ Simulação de cálculo de impostos</li>
                <li>✅ 100% seguro e privado</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;