"""Testes de integração com o banco de dados MongoDB"""
import pytest
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

class TestDatabaseOperations:
    """Testes de operações no banco de dados"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup e cleanup para cada teste"""
        self.client = MongoClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.users = self.db.users
        yield
        # Cleanup - remove dados de teste
        self.users.delete_many({'email': {'$regex': 'teste_db_.*'}})
        self.client.close()
    
    def test_insert_user(self):
        """Testa inserção de usuário no banco"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            'nome': 'Teste DB',
            'email': f'teste_db_{timestamp}@teste.com',
            'cpf': '12345678900',
            'password_hash': generate_password_hash('senha123')
        }
        
        result = self.users.insert_one(user_data)
        
        assert result.inserted_id is not None
        
        # Verifica se foi inserido
        found = self.users.find_one({'_id': result.inserted_id})
        assert found is not None
        assert found['email'] == user_data['email']
    
    def test_find_user_by_email(self):
        """Testa busca de usuário por e-mail"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        email = f'teste_db_{timestamp}@teste.com'
        
        user_data = {
            'nome': 'Teste DB',
            'email': email,
            'cpf': '12345678900',
            'password_hash': generate_password_hash('senha123')
        }
        
        self.users.insert_one(user_data)
        
        # Busca usuário
        found = self.users.find_one({'email': email})
        
        assert found is not None
        assert found['nome'] == 'Teste DB'
    
    def test_update_reset_token(self):
        """Testa adição de token de redefinição"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        email = f'teste_db_{timestamp}@teste.com'
        
        user_data = {
            'nome': 'Teste DB',
            'email': email,
            'cpf': '12345678900',
            'password_hash': generate_password_hash('senha123')
        }
        
        result = self.users.insert_one(user_data)
        
        # Adiciona token de redefinição
        reset_token = '123456'
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        self.users.update_one(
            {'_id': result.inserted_id},
            {'$set': {
                'reset_token': reset_token,
                'reset_token_expires': expires_at
            }}
        )
        
        # Verifica se foi atualizado
        found = self.users.find_one({'_id': result.inserted_id})
        
        assert 'reset_token' in found
        assert found['reset_token'] == reset_token
        assert 'reset_token_expires' in found
    
    def test_remove_reset_token(self):
        """Testa remoção de token após uso"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        email = f'teste_db_{timestamp}@teste.com'
        
        user_data = {
            'nome': 'Teste DB',
            'email': email,
            'cpf': '12345678900',
            'password_hash': generate_password_hash('senha123'),
            'reset_token': '123456',
            'reset_token_expires': datetime.utcnow() + timedelta(minutes=15)
        }
        
        result = self.users.insert_one(user_data)
        
        # Remove token
        self.users.update_one(
            {'_id': result.inserted_id},
            {'$unset': {
                'reset_token': '',
                'reset_token_expires': ''
            }}
        )
        
        # Verifica se foi removido
        found = self.users.find_one({'_id': result.inserted_id})
        
        assert 'reset_token' not in found
        assert 'reset_token_expires' not in found
