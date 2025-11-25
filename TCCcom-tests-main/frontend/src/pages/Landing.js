import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Landing.css';

function Landing() {
  const navigate = useNavigate();
  const [animatedText, setAnimatedText] = useState('');
  const fullText = 'TAXXAT';

  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      if (index <= fullText.length) {
        setAnimatedText(fullText.slice(0, index));
        index++;
      } else {
        clearInterval(interval);
      }
    }, 200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="landing">
      {/* Floating chatbot animations */}
      <div className="floating-elements">
        <div className="float-icon chat-bubble-float">💬</div>
        <div className="float-icon calculator-float">🧮</div>
        <div className="float-icon document-float">📄</div>
        <div className="float-icon money-float">💰</div>
        <div className="float-icon ai-float">🤖</div>
      </div>

      {/* Header com Logo */}
      <header className="landing-header">
        <div className="container">
          <div className="header-content">
            <div className="logo-container">
              <img src={`${process.env.PUBLIC_URL}/images/logo.png`} alt="TAXXAT Logo" className="logo-img" />
              <span className="logo-text-header">{animatedText}</span>
            </div>
            <nav className="nav">
              <a href="#sobre" className="nav-link">Sobre</a>
              <a href="#funcionalidades" className="nav-link">Funcionalidades</a>
              <button className="btn btn-outline" onClick={() => navigate('/login')}>Entrar</button>
              <button className="btn btn-primary" onClick={() => navigate('/register')}>Cadastrar</button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section com Banner */}
      <section className="hero" style={{backgroundImage: `url(${process.env.PUBLIC_URL}/images/banner.jpg)`}}>
        <div className="hero-overlay">
          <div className="container">
            <div className="hero-content">
              <div className="hero-text">
                {/* Badge animado */}
                <div className="hero-badge">
                  <span className="badge-icon">🤖</span>
                  <span className="badge-text">IA + Imposto de Renda</span>
                </div>
                
                <h1 className="hero-title">
                  Simplifique sua
                  <span className="gradient-text"> Declaração de Imposto de Renda</span>
                  <span className="typing-cursor">|</span>
                </h1>
                <p className="hero-description">
                  <span className="highlight-text">TAXXAT</span> é o assistente inteligente que usa IA para tornar sua declaração de IR
                  rápida, simples e sem complicações.
                </p>
                <div className="hero-buttons">
                  <button className="btn btn-primary btn-large pulse-btn" onClick={() => navigate('/register')}>
                    <span className="btn-icon">🚀</span>
                    Começar Agora - É Grátis!
                  </button>
                  <button className="btn btn-outline-white btn-large" onClick={() => navigate('/login')}>
                    <span className="btn-icon">👤</span>
                    Já tenho conta
                  </button>
                </div>

                {/* Stats rápidos */}
                <div className="hero-stats">
                  <div className="stat-item">
                    <span className="stat-number">99%</span>
                    <span className="stat-label">Precisão</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-number">24/7</span>
                    <span className="stat-label">Disponível</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-number">100%</span>
                    <span className="stat-label">Seguro</span>
                  </div>
                </div>
              </div>

              {/* Chatbot Animation */}
              <div className="hero-chatbot">
                <div className="chatbot-window">
                  <div className="chatbot-header">
                    <div className="chatbot-avatar">🤖</div>
                    <div className="chatbot-title">
                      <strong>TAXXAT Assistant</strong>
                      <span className="status-online">● Online</span>
                    </div>
                  </div>
                  <div className="chatbot-messages">
                    <div className="message bot-message animate-in">
                      <span className="message-icon">🤖</span>
                      <div className="message-bubble">
                        Olá! Posso te ajudar com sua declaração de IR?
                      </div>
                    </div>
                    <div className="message user-message animate-in delay-1">
                      <div className="message-bubble">
                        Quem precisa declarar IR em 2025?
                      </div>
                      <span className="message-icon">👤</span>
                    </div>
                    <div className="message bot-message animate-in delay-2">
                      <span className="message-icon">🤖</span>
                      <div className="message-bubble">
                        Pessoas com renda anual acima de R$ 30.639,90 devem declarar! 📊
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="funcionalidades" className="features">
        <div className="container">
          <div className="section-header">
            <span className="section-badge">Nossas Funcionalidades</span>
            <h2 className="section-title">Como o TAXXAT pode te ajudar</h2>
            <p className="section-subtitle">Tecnologia de ponta para simplificar seu Imposto de Renda</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">💬</div>
                <div className="feature-badge">IA</div>
              </div>
              <h3>Chatbot Inteligente</h3>
              <p>Tire todas suas dúvidas sobre Imposto de Renda com nosso assistente virtual disponível 24 horas por dia.</p>
              <div className="feature-link">Saiba mais →</div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">📄</div>
                <div className="feature-badge">Auto</div>
              </div>
              <h3>Upload de Documentos</h3>
              <p>Envie seus comprovantes e recibos. Nossa IA analisa e extrai as informações automaticamente.</p>
              <div className="feature-link">Saiba mais →</div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">🧮</div>
                <div className="feature-badge">Preciso</div>
              </div>
              <h3>Calculadora de IR</h3>
              <p>Simule quanto você vai pagar ou receber de restituição de forma rápida e precisa.</p>
              <div className="feature-link">Saiba mais →</div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">🔒</div>
                <div className="feature-badge">LGPD</div>
              </div>
              <h3>Segurança Total</h3>
              <p>Seus dados são criptografados e protegidos seguindo as normas da LGPD.</p>
              <div className="feature-link">Saiba mais →</div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">📊</div>
                <div className="feature-badge">Visual</div>
              </div>
              <h3>Painel Completo</h3>
              <p>Acompanhe todo seu histórico de declarações e simulações em um só lugar.</p>
              <div className="feature-link">Saiba mais →</div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">⚡</div>
                <div className="feature-badge">Fast</div>
              </div>
              <h3>Rápido e Fácil</h3>
              <p>Interface moderna e intuitiva. Declare seu IR em minutos, não em horas.</p>
              <div className="feature-link">Saiba mais →</div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section com imagens */}
      <section id="sobre" className="about">
        <div className="container">
          <div className="about-grid">
            <div className="about-image">
              <div className="image-wrapper">
                <img src={`${process.env.PUBLIC_URL}/images/imgtexto.png`} alt="TAXXAT IA" className="about-img" />
                <div className="image-overlay">
                  <div className="overlay-icon">🤖</div>
                  <div className="overlay-text">IA Especializada</div>
                </div>
              </div>
            </div>
            <div className="about-text">
              <span className="section-badge">Tecnologia de Ponta</span>
              <h2>Inteligência Artificial para facilitar sua vida</h2>
              <p>
                O <strong>TAXXAT</strong> foi desenvolvido com a mais moderna tecnologia em Inteligência Artificial
                para transformar a complexa tarefa de declarar Imposto de Renda em algo simples e rápido.
              </p>
              <ul className="about-list">
                <li><span className="list-icon">✅</span> Baseado nas regras oficiais da Receita Federal</li>
                <li><span className="list-icon">✅</span> Interface intuitiva e moderna</li>
                <li><span className="list-icon">✅</span> Segurança e privacidade garantidas</li>
                <li><span className="list-icon">✅</span> Suporte 24/7 com IA especializada</li>
              </ul>
            </div>
          </div>

          <div className="about-grid about-grid-reverse">
            <div className="about-text">
              <span className="section-badge">Assistente Virtual</span>
              <h2>Assistente Virtual Especializado em IR</h2>
              <p>
                Nossa IA foi treinada especificamente para entender as regras e legislação
                do Imposto de Renda brasileiro, respondendo suas dúvidas de forma clara e precisa.
              </p>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">📈</div>
                  <h3>99%</h3>
                  <p>Precisão nos cálculos</p>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">🕐</div>
                  <h3>24/7</h3>
                  <p>Suporte disponível</p>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">🔐</div>
                  <h3>100%</h3>
                  <p>Seguro e confiável</p>
                </div>
              </div>
            </div>
            <div className="about-image">
              <div className="image-wrapper">
                <img src={`${process.env.PUBLIC_URL}/images/imgtexto2.png`} alt="Assistente Virtual" className="about-img" />
                <div className="image-overlay">
                  <div className="overlay-icon">🧮</div>
                  <div className="overlay-text">Cálculo Preciso</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="container">
          <div className="cta-content">
            <div className="cta-icon-group">
              <span className="cta-icon">🤖</span>
              <span className="cta-icon">📊</span>
              <span className="cta-icon">💰</span>
            </div>
            <h2>Pronto para simplificar sua declaração de IR?</h2>
            <p>Junte-se a milhares de pessoas que já estão usando o TAXXAT.</p>
            <button className="btn btn-white btn-large pulse-btn" onClick={() => navigate('/register')}>
              <span className="btn-icon">🚀</span>
              Começar Agora - É Grátis!
            </button>
            <div className="cta-features">
              <span>✓ Sem cartão de crédito</span>
              <span>✓ Acesso imediato</span>
              <span>✓ Suporte 24/7</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <img src={`${process.env.PUBLIC_URL}/images/logo.png`} alt="TAXXAT" className="footer-logo" />
              <p>Assistente Virtual de Imposto de Renda com IA</p>
              <div className="footer-badges">
                <span className="footer-badge">🤖 IA Powered</span>
                <span className="footer-badge">🔒 100% Seguro</span>
              </div>
            </div>
            <div className="footer-links">
              <h4>Contato</h4>
              <p>📧 suporte@taxxat.com.br</p>
              <p>📱 (11) 99999-9999</p>
              <div className="social-icons">
                <span className="social-icon">📘</span>
                <span className="social-icon">📷</span>
                <span className="social-icon">🐦</span>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© 2025 TAXXAT. Todos os direitos reservados. | Powered by AI 🤖</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Landing;