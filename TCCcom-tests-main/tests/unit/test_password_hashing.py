"""Testes unitários para hash de senhas"""
import pytest
from werkzeug.security import generate_password_hash, check_password_hash

class TestPasswordHashing:
    """Testes para hashing de senhas"""
    
    def test_password_hash_generation(self):
        """Testa geração de hash de senha"""
        password = 'minhaSenha123'
        hashed = generate_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20
    
    def test_password_verification_success(self):
        """Testa verificação bem-sucedida de senha"""
        password = 'minhaSenha123'
        hashed = generate_password_hash(password)
        
        assert check_password_hash(hashed, password) is True
    
    def test_password_verification_failure(self):
        """Testa verificação com senha incorreta"""
        password = 'minhaSenha123'
        wrong_password = 'senhaErrada'
        hashed = generate_password_hash(password)
        
        assert check_password_hash(hashed, wrong_password) is False
    
    def test_same_password_different_hashes(self):
        """Testa que a mesma senha gera hashes diferentes (salt)"""
        password = 'minhaSenha123'
        hash1 = generate_password_hash(password)
        hash2 = generate_password_hash(password)
        
        assert hash1 != hash2
        assert check_password_hash(hash1, password) is True
        assert check_password_hash(hash2, password) is True
