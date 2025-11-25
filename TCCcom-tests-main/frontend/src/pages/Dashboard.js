import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('chatbot');
  const [loading, setLoading] = useState(true);

  // Chatbot state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Documents state
  const [documents, setDocuments] = useState([]);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);

  // Simulation state - REMOVIDO

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkAuth = async () => {
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      } else {
        navigate('/login');
      }
    } catch (error) {
      navigate('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
      localStorage.removeItem('user');
      navigate('/login');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      localStorage.removeItem('user');
      navigate('/login');
    }
  };

  // ==================== CHATBOT ====================

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || chatLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);

    try {
      const response = await axios.post(
        `${API}/chat`,
        { message: userMessage },
        { withCredentials: true }
      );

      // Add bot response to chat
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: response.data.response }
      ]);
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: 'Desculpe, ocorreu um erro. Tente novamente.' }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API}/chatbot/history`, {
        withCredentials: true
      });
      
      const formattedMessages = [];
      response.data.conversations.reverse().forEach(conv => {
        formattedMessages.push(
          { role: 'user', content: conv.user_message },
          { role: 'bot', content: conv.bot_response }
        );
      });
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'chatbot' && messages.length === 0) {
      loadChatHistory();
    }
  }, [activeTab]);

  // ==================== DOCUMENTS ====================

  const handleFileChange = (e) => {
    setUploadFile(e.target.files[0]);
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploadLoading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      const response = await axios.post(
        `${API}/documents/upload`,
        formData,
        {
          withCredentials: true,
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );

      alert('Documento enviado com sucesso!');
      setUploadFile(null);
      loadDocuments();
    } catch (error) {
      console.error('Erro ao enviar documento:', error);
      alert(error.response?.data?.error || 'Erro ao enviar documento');
    } finally {
      setUploadLoading(false);
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await axios.get(`${API}/documents/`, {
        withCredentials: true
      });
      setDocuments(response.data.documents);
    } catch (error) {
      console.error('Erro ao carregar documentos:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'documents') {
      loadDocuments();
    }
  }, [activeTab]);

  // ==================== SIMULATION - REMOVIDO ====================

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loader"></div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">🤖</span>
            <span className="logo-text">TAXXAT</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === 'chatbot' ? 'active' : ''}`}
            onClick={() => setActiveTab('chatbot')}
          >
            <span className="nav-icon">💬</span>
            <span>Chatbot</span>
          </button>
          <button
            className={`nav-item ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            <span className="nav-icon">📄</span>
            <span>Documentos</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">{user?.nome?.charAt(0).toUpperCase()}</div>
            <div className="user-details">
              <p className="user-name">{user?.nome}</p>
              <p className="user-email">{user?.email}</p>
            </div>
          </div>
          <button className="btn-logout" onClick={handleLogout}>
            Sair 🚪
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* CHATBOT TAB */}
        {activeTab === 'chatbot' && (
          <div className="content-section chatbot-section">
            <div className="section-header">
              <h2>🤖 Assistente Virtual de IR</h2>
              <p>Tire suas dúvidas sobre Imposto de Renda com nossa IA</p>
            </div>

            <div className="chat-container">
              <div className="messages-container">
                {messages.length === 0 && (
                  <div className="empty-state">
                    <span className="empty-icon">👋</span>
                    <h3>Olá! Como posso ajudar?</h3>
                    <p>Faça perguntas sobre Imposto de Renda</p>
                    <div className="suggestions">
                      <button onClick={() => setInputMessage('Quem precisa declarar IR em 2025?')}>
                        Quem precisa declarar?
                      </button>
                      <button onClick={() => setInputMessage('Quais são as deduções permitidas?')}>
                        Deduções permitidas
                      </button>
                      <button onClick={() => setInputMessage('Qual o prazo para declarar?')}>
                        Prazo de declaração
                      </button>
                    </div>
                  </div>
                )}

                {messages.map((msg, index) => (
                  <div key={index} className={`message ${msg.role}`}>
                    <div className="message-avatar">
                      {msg.role === 'bot' ? '🤖' : '👤'}
                    </div>
                    <div className="message-content">
                      <p>{msg.content}</p>
                    </div>
                  </div>
                ))}

                {chatLoading && (
                  <div className="message bot">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              <form onSubmit={sendMessage} className="chat-input-form">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Digite sua pergunta..."
                  disabled={chatLoading}
                />
                <button type="submit" disabled={chatLoading || !inputMessage.trim()}>
                  ➤
                </button>
              </form>
            </div>
          </div>
        )}

        {/* DOCUMENTS TAB */}
        {activeTab === 'documents' && (
          <div className="content-section documents-section">
            <div className="section-header">
              <h2>📄 Meus Documentos</h2>
              <p>Envie seus comprovantes e recibos para análise</p>
            </div>

            <div className="upload-area">
              <form onSubmit={handleFileUpload} className="upload-form">
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    id="file"
                    onChange={handleFileChange}
                    accept=".pdf,.jpg,.jpeg,.png,.txt"
                  />
                  <label htmlFor="file" className="file-input-label">
                    {uploadFile ? (
                      <>
                        <span>📄 {uploadFile.name}</span>
                      </>
                    ) : (
                      <>
                        <span className="upload-icon">⬆️</span>
                        <span>Clique para selecionar um arquivo</span>
                        <span className="file-types">PDF, JPG, PNG ou TXT</span>
                      </>
                    )}
                  </label>
                </div>
                {uploadFile && (
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={uploadLoading}
                  >
                    {uploadLoading ? 'Enviando...' : 'Enviar Documento'}
                  </button>
                )}
              </form>
            </div>

            <div className="documents-list">
              <h3>Documentos Enviados</h3>
              {documents.length === 0 ? (
                <div className="empty-state">
                  <span className="empty-icon">📂</span>
                  <p>Nenhum documento enviado ainda</p>
                </div>
              ) : (
                <div className="documents-grid">
                  {documents.map((doc) => (
                    <div key={doc.id} className="document-card">
                      <div className="doc-icon">📄</div>
                      <div className="doc-info">
                        <h4>{doc.original_filename}</h4>
                        <p className="doc-date">
                          {new Date(doc.upload_date).toLocaleDateString('pt-BR')}
                        </p>
                        <span className="doc-status">{doc.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* SIMULATION TAB - REMOVIDO */}
      </main>
    </div>
  );
}

export default Dashboard;