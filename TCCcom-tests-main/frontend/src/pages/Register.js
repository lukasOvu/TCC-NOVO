import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    cpf: '',
    senha: '',
    confirmarSenha: ''
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

    // Validate passwords match
    if (formData.senha !== formData.confirmarSenha) {
      setError('As senhas não coincidem');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(
        `${API}/auth/register`,
        {
          nome: formData.nome,
          email: formData.email,
          senha: formData.senha,
          cpf: formData.cpf
        },
        { withCredentials: true }
      );

      // Auto login after register
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao criar conta');
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

            <h1 className="auth-title">Criar sua conta</h1>
            <p className="auth-subtitle">Comece a usar o assistente de IR gratuitamente.</p>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="nome">Nome Completo</label>
                <input
                  type="text"
                  id="nome"
                  name="nome"
                  value={formData.nome}
                  onChange={handleChange}
                  placeholder="Seu nome completo"
                  required
                />
              </div>

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
                <label htmlFor="cpf">CPF (opcional)</label>
                <input
                  type="text"
                  id="cpf"
                  name="cpf"
                  value={formData.cpf}
                  onChange={handleChange}
                  placeholder="000.000.000-00"
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
                  placeholder="Mínimo 6 caracteres"
                  required
                  minLength="6"
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirmarSenha">Confirmar Senha</label>
                <input
                  type="password"
                  id="confirmarSenha"
                  name="confirmarSenha"
                  value={formData.confirmarSenha}
                  onChange={handleChange}
                  placeholder="Digite a senha novamente"
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? 'Criando conta...' : 'Cadastrar'}
              </button>
            </form>

            <div className="auth-links">
              <p>
                Já tem uma conta?{' '}
                <button onClick={() => navigate('/login')} className="link-button">
                  Entre aqui
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
              <h2>🎯 Por que usar o TAXXAT?</h2>
              <ul className="banner-list">
                <li>🤖 IA especializada em Imposto de Renda</li>
                <li>📊 Cálculos precisos e confiáveis</li>
                <li>🔐 Seus dados 100% protegidos</li>
                <li>⚡ Interface moderna e intuitiva</li>
                <li>📱 Acesse de qualquer dispositivo</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;