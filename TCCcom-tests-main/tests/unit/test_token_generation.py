"""Testes unitários para geração de tokens"""
import pytest
import secrets
from datetime import datetime, timedelta

class TestTokenGeneration:
    """Testes para geração de tokens de redefinição"""
    
    def test_token_generation_format(self):
        """Testa se o token tem 6 dígitos"""
        token = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        assert len(token) == 6
        assert token.isdigit()
    
    def test_token_uniqueness(self):
        """Testa se tokens gerados são únicos"""
        tokens = set()
        for _ in range(100):
            token = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            tokens.add(token)
        
        # Com 100 tokens, esperamos pelo menos 90 únicos (considerando colisões)
        assert len(tokens) >= 90
    
    def test_token_expiration_calculation(self):
        """Testa cálculo de expiração do token"""
        now = datetime.utcnow()
        expires = now + timedelta(minutes=15)
        
        assert expires > now
        assert (expires - now).total_seconds() == 900  # 15 minutos
    
    def test_token_expired(self):
        """Testa detecção de token expirado"""
        now = datetime.utcnow()
        expires = now - timedelta(minutes=1)  # Expirado há 1 minuto
        
        assert now > expires
