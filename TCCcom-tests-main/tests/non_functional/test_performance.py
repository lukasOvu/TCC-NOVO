"""Testes não funcionais - Performance"""
import pytest
import requests
import time
from datetime import datetime
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8001')
API_URL = f"{BACKEND_URL}/api"

class TestPerformance:
    """Testes de performance da API"""
    
    def test_api_response_time_login(self):
        """Testa tempo de resposta da API de login"""
        # Registra usuário primeiro
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            'nome': 'Teste Perf',
            'email': f'perf_{timestamp}@teste.com',
            'cpf': '12345678900',
            'senha': 'senha123'
        }
        requests.post(f"{API_URL}/auth/register", json=user_data)
        
        # Mede tempo de login
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/auth/login",
            json={'email': user_data['email'], 'senha': user_data['senha']}
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Em milissegundos
        
        assert response.status_code == 200
        assert response_time < 2000, f"Login demorou {response_time}ms (esperado < 2000ms)"
        print(f"\nTempo de resposta do login: {response_time:.2f}ms")
    
    def test_api_response_time_register(self):
        """Testa tempo de resposta da API de registro"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            'nome': 'Teste Perf',
            'email': f'perf_reg_{timestamp}@teste.com',
            'cpf': '12345678900',
            'senha': 'senha123'
        }
        
        start_time = time.time()
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 201
        assert response_time < 3000, f"Registro demorou {response_time}ms (esperado < 3000ms)"
        print(f"\nTempo de resposta do registro: {response_time:.2f}ms")
    
    def test_api_response_time_forgot_password(self):
        """Testa tempo de resposta da API de esqueceu senha"""
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/auth/forgot-password",
            json={'email': 'teste@teste.com'}
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time < 2000, f"Forgot password demorou {response_time}ms (esperado < 2000ms)"
        print(f"\nTempo de resposta forgot password: {response_time:.2f}ms")
    
    def test_concurrent_requests(self):
        """Testa performance com requisições concorrentes"""
        import concurrent.futures
        
        def make_request():
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
            user_data = {
                'nome': 'Teste Concorrente',
                'email': f'concurrent_{timestamp}@teste.com',
                'cpf': '12345678900',
                'senha': 'senha123'
            }
            start = time.time()
            response = requests.post(f"{API_URL}/auth/register", json=user_data)
            end = time.time()
            return (end - start) * 1000, response.status_code
        
        # Executa 10 requisições concorrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Verifica resultados
        response_times = [r[0] for r in results]
        status_codes = [r[1] for r in results]
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        print(f"\nRequisições concorrentes:")
        print(f"  Tempo médio: {avg_time:.2f}ms")
        print(f"  Tempo máximo: {max_time:.2f}ms")
        
        assert all(code in [201, 409] for code in status_codes)
        assert avg_time < 5000, f"Tempo médio muito alto: {avg_time}ms"

class TestDatabasePerformance:
    """Testes de performance do banco de dados"""
    
    def test_query_performance(self):
        """Testa performance de consulta no banco"""
        from pymongo import MongoClient
        
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.getenv('DB_NAME', 'test_database')
        
        client = MongoClient(mongo_url)
        db = client[db_name]
        users = db.users
        
        # Cria usuário de teste
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        email = f'perf_query_{timestamp}@teste.com'
        users.insert_one({
            'nome': 'Teste Perf',
            'email': email,
            'cpf': '12345678900'
        })
        
        # Mede tempo de consulta
        start_time = time.time()
        result = users.find_one({'email': email})
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000
        
        assert result is not None
        assert query_time < 100, f"Consulta demorou {query_time}ms (esperado < 100ms)"
        print(f"\nTempo de consulta no banco: {query_time:.2f}ms")
        
        # Cleanup
        users.delete_one({'email': email})
        client.close()
