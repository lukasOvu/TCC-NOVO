import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function ResetPassword() {
  const navigate = useNavigate();
  const location = useLocation();
  const emailFromState = location.state?.email || '';
  
  const [formData, setFormData] = useState({
    email: emailFromState,
    token: '',
    novaSenha: '',
    confirmarSenha: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

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
    setSuccess(false);

    // Valida se as senhas coincidem
    if (formData.novaSenha !== formData.confirmarSenha) {
      setError('As senhas não coincidem');
      setLoading(false);
      return;
    }

    // Valida tamanho mínimo da senha
    if (formData.novaSenha.length < 6) {
      setError('A senha deve ter no mínimo 6 caracteres');
      setLoading(false);
      return;
    }

    try {
      await axios.post(`${API}/auth/reset-password`, {
        email: formData.email,
        token: formData.token,
        new_password: formData.novaSenha
      });
      
      setSuccess(true);
      
      // Redireciona para login após 2 segundos
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao redefinir senha');
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

            <h1 className="auth-title">Redefinir Senha</h1>
            <p className="auth-subtitle">Digite o código recebido por e-mail e sua nova senha.</p>

            {error && (
              <div className="error-message" data-testid="error-message">
                {error}
              </div>
            )}

            {success && (
              <div className="success-message" data-testid="success-message">
                ✅ Senha redefinida com sucesso! Redirecionando...
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
                  data-testid="email-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="token">Código de Verificação</label>
                <input
                  type="text"
                  id="token"
                  name="token"
                  value={formData.token}
                  onChange={handleChange}
                  placeholder="Digite o código de 6 dígitos"
                  required
                  maxLength="6"
                  data-testid="token-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="novaSenha">Nova Senha</label>
                <input
                  type="password"
                  id="novaSenha"
                  name="novaSenha"
                  value={formData.novaSenha}
                  onChange={handleChange}
                  placeholder="Mínimo 6 caracteres"
                  required
                  minLength="6"
                  data-testid="new-password-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirmarSenha">Confirmar Nova Senha</label>
                <input
                  type="password"
                  id="confirmarSenha"
                  name="confirmarSenha"
                  value={formData.confirmarSenha}
                  onChange={handleChange}
                  placeholder="Digite a senha novamente"
                  required
                  data-testid="confirm-password-input"
                />
              </div>

              <button 
                type="submit" 
                className="btn btn-primary btn-full" 
                disabled={loading}
                data-testid="submit-button"
              >
                {loading ? 'Redefinindo...' : 'Redefinir Senha'}
              </button>
            </form>

            <div className="auth-links">
              <button onClick={() => navigate('/forgot-password')} className="link-button" data-testid="resend-code">
                ← Reenviar código
              </button>
              <button onClick={() => navigate('/login')} className="link-button" data-testid="back-to-login">
                Voltar para Login
              </button>
            </div>
          </div>
        </div>

        <div className="auth-banner-section">
          <div className="banner-overlay">
            <div className="banner-content">
              <h2>🔑 Nova Senha</h2>
              <ul className="banner-list">
                <li>✅ Use o código do seu e-mail</li>
                <li>🔒 Crie uma senha forte</li>
                <li>⏱️ Código válido por 15 minutos</li>
                <li>✨ Acesse sua conta novamente</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResetPassword;
