"""Testes de integração para APIs de autenticação"""
import pytest
import requests
import os
from datetime import datetime

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8001')
API_URL = f"{BACKEND_URL}/api"

class TestAuthenticationAPI:
    """Testes de integração para autenticação"""
    
    def test_register_user_success(self):
        """Testa registro de usuário com sucesso"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            'nome': 'Teste Usuario',
            'email': f'teste_{timestamp}@teste.com',
            'cpf': '12345678900',
            'senha': 'senha123'
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert 'user' in data
        assert data['user']['email'] == user_data['email']
    
    def test_register_duplicate_email(self):
        """Testa registro com e-mail duplicado"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            'nome': 'Teste Usuario',
            'email': f'duplicado_{timestamp}@teste.com',
            'cpf': '12345678900',
            'senha': 'senha123'
        }
        
        # Primeiro registro
        requests.post(f"{API_URL}/auth/register", json=user_data)
        
        # Segundo registro (deve falhar)
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        
        assert response.status_code == 409
        assert 'error' in response.json()
    
    def test_register_missing_fields(self):
        """Testa registro sem campos obrigatórios"""
        user_data = {'email': 'teste@teste.com'}
        
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        
        assert response.status_code == 400
    
    def test_login_success(self):
        """Testa login com sucesso"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            'nome': 'Teste Usuario',
            'email': f'login_{timestamp}@teste.com',
            'cpf': '12345678900',
            'senha': 'senha123'
        }
        
        # Registra usuário
        requests.post(f"{API_URL}/auth/register", json=user_data)
        
        # Tenta login
        login_data = {'email': user_data['email'], 'senha': user_data['senha']}
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert 'user' in data
        assert data['user']['email'] == user_data['email']
    
    def test_login_wrong_password(self):
        """Testa login com senha incorreta"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            'nome': 'Teste Usuario',
            'email': f'wrongpass_{timestamp}@teste.com',
            'cpf': '12345678900',
            'senha': 'senha123'
        }
        
        # Registra usuário
        requests.post(f"{API_URL}/auth/register", json=user_data)
        
        # Tenta login com senha errada
        login_data = {'email': user_data['email'], 'senha': 'senhaErrada'}
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        assert response.status_code == 401

class TestPasswordResetAPI:
    """Testes de integração para redefinição de senha"""
    
    def test_forgot_password_success(self):
        """Testa solicitação de redefinição de senha"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            'nome': 'Teste Usuario',
            'email': f'forgot_{timestamp}@teste.com',
            'cpf': '12345678900',
            'senha': 'senha123'
        }
        
        # Registra usuário
        requests.post(f"{API_URL}/auth/register", json=user_data)
        
        # Solicita redefinição
        response = requests.post(
            f"{API_URL}/auth/forgot-password",
            json={'email': user_data['email']}
        )
        
        assert response.status_code == 200
        assert 'message' in response.json()
    
    def test_forgot_password_nonexistent_email(self):
        """Testa solicitação com e-mail não existente"""
        response = requests.post(
            f"{API_URL}/auth/forgot-password",
            json={'email': 'naoexiste@teste.com'}
        )
        
        # Por segurança, retorna 200 mesmo se e-mail não existe
        assert response.status_code == 200
    
    def test_reset_password_invalid_token(self):
        """Testa redefinição com token inválido"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            'nome': 'Teste Usuario',
            'email': f'invalidtoken_{timestamp}@teste.com',
            'cpf': '12345678900',
            'senha': 'senha123'
        }
        
        # Registra usuário
        requests.post(f"{API_URL}/auth/register", json=user_data)
        
        # Tenta redefinir com token inválido
        reset_data = {
            'email': user_data['email'],
            'token': '999999',
            'new_password': 'novaSenha123'
        }
        response = requests.post(f"{API_URL}/auth/reset-password", json=reset_data)
        
        assert response.status_code == 400
    
    def test_reset_password_missing_fields(self):
        """Testa redefinição sem campos obrigatórios"""
        response = requests.post(
            f"{API_URL}/auth/reset-password",
            json={'email': 'teste@teste.com'}
        )
        
        assert response.status_code == 400
