"""Teste de carga usando Locust

Para executar:
    locust -f tests/non_functional/locustfile.py --host=https://senha-redefinir.preview.emergentagent.com

Depóis acesse: http://localhost:8089
"""

from locust import HttpUser, task, between
import random
import string
from datetime import datetime

class TaxChatUser(HttpUser):
    """Simula um usuário da aplicação TAXXAT"""
    wait_time = between(1, 3)  # Espera entre 1-3 segundos entre requisições
    
    def on_start(self):
        """Executado quando o usuário inicia"""
        self.email = None
        self.password = 'senha123'
    
    @task(3)
    def register_user(self):
        """Registra um novo usuário (peso 3)"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        random_str = ''.join(random.choices(string.ascii_lowercase, k=5))
        
        self.email = f'load_{timestamp}_{random_str}@teste.com'
        
        self.client.post("/api/auth/register", json={
            'nome': f'Usuario Teste {random_str}',
            'email': self.email,
            'cpf': '12345678900',
            'senha': self.password
        })
    
    @task(5)
    def login_user(self):
        """Faz login com usuário existente (peso 5)"""
        if not self.email:
            # Cria usuário primeiro
            self.register_user()
        
        self.client.post("/api/auth/login", json={
            'email': self.email,
            'senha': self.password
        })
    
    @task(2)
    def forgot_password(self):
        """Solicita redefinição de senha (peso 2)"""
        if not self.email:
            self.register_user()
        
        self.client.post("/api/auth/forgot-password", json={
            'email': self.email
        })
    
    @task(1)
    def check_session(self):
        """Verifica sessão (peso 1)"""
        self.client.get("/api/check_session")

class WebsiteUser(HttpUser):
    """Simula usuário navegando no site"""
    wait_time = between(2, 5)
    
    @task(5)
    def visit_login_page(self):
        """Visita página de login"""
        self.client.get("/login")
    
    @task(3)
    def visit_register_page(self):
        """Visita página de registro"""
        self.client.get("/register")
    
    @task(2)
    def visit_forgot_password(self):
        """Visita página de esqueceu senha"""
        self.client.get("/forgot-password")
    
    @task(1)
    def visit_reset_password(self):
        """Visita página de redefinir senha"""
        self.client.get("/reset-password")
