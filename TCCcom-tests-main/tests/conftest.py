"""Configuração compartilhada para todos os testes"""
import pytest
import sys
import os
from pathlib import Path

# Adiciona o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

@pytest.fixture
def test_user_data():
    """Dados de teste para usuário"""
    return {
        'nome': 'Usuario Teste',
        'email': 'teste@teste.com',
        'cpf': '12345678900',
        'senha': 'senha123'
    }

@pytest.fixture
def test_reset_data():
    """Dados de teste para redefinição de senha"""
    return {
        'email': 'teste@teste.com',
        'token': '123456',
        'new_password': 'novaSenha123'
    }
