"""Testes de interface (GUI) para fluxos de autenticação usando Playwright"""
import pytest
from playwright.sync_api import Page, expect
import os
from datetime import datetime

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8001')

class TestAuthenticationUI:
    """Testes de interface para autenticação"""
    
    def test_login_page_loads(self, page: Page):
        """Testa se a página de login carrega corretamente"""
        page.goto(f"{FRONTEND_URL}/login")
        
        # Verifica elementos da página
        expect(page.locator('h1')).to_contain_text('Entrar na sua conta')
        expect(page.locator('input[name="email"]')).to_be_visible()
        expect(page.locator('input[name="senha"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()
    
    def test_login_forgot_password_link(self, page: Page):
        """Testa se o link 'Esqueceu sua senha?' está presente"""
        page.goto(f"{FRONTEND_URL}/login")
        
        forgot_link = page.locator('[data-testid="forgot-password-link"]')
        expect(forgot_link).to_be_visible()
        expect(forgot_link).to_contain_text('Esqueceu sua senha?')
    
    def test_login_to_register_navigation(self, page: Page):
        """Testa navegação de login para registro"""
        page.goto(f"{FRONTEND_URL}/login")
        
        # Clica no link de cadastro
        page.locator('text=Cadastre-se aqui').click()
        
        # Verifica se está na página de registro
        expect(page).to_have_url(f"{FRONTEND_URL}/register")
        expect(page.locator('h1')).to_contain_text('Criar sua conta')
    
    def test_register_page_loads(self, page: Page):
        """Testa se a página de registro carrega corretamente"""
        page.goto(f"{FRONTEND_URL}/register")
        
        # Verifica elementos da página
        expect(page.locator('h1')).to_contain_text('Criar sua conta')
        expect(page.locator('input[name="nome"]')).to_be_visible()
        expect(page.locator('input[name="email"]')).to_be_visible()
        expect(page.locator('input[name="cpf"]')).to_be_visible()
        expect(page.locator('input[name="senha"]')).to_be_visible()
        expect(page.locator('input[name="confirmarSenha"]')).to_be_visible()
    
    def test_register_password_mismatch(self, page: Page):
        """Testa mensagem de erro quando senhas não coincidem"""
        page.goto(f"{FRONTEND_URL}/register")
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Preenche formulário
        page.fill('input[name="nome"]', 'Teste Usuario')
        page.fill('input[name="email"]', f'teste_{timestamp}@teste.com')
        page.fill('input[name="senha"]', 'senha123')
        page.fill('input[name="confirmarSenha"]', 'senha456')
        
        # Submete formulário
        page.click('button[type="submit"]')
        
        # Verifica mensagem de erro
        error = page.locator('.error-message')
        expect(error).to_be_visible()
        expect(error).to_contain_text('As senhas não coincidem')

class TestPasswordResetUI:
    """Testes de interface para redefinição de senha"""
    
    def test_forgot_password_page_loads(self, page: Page):
        """Testa se a página 'Esqueceu a senha' carrega corretamente"""
        page.goto(f"{FRONTEND_URL}/forgot-password")
        
        # Verifica elementos da página
        expect(page.locator('h1')).to_contain_text('Esqueceu sua senha?')
        expect(page.locator('input[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('button[data-testid="submit-button"]')).to_be_visible()
    
    def test_forgot_password_back_to_login(self, page: Page):
        """Testa navegação de volta para login"""
        page.goto(f"{FRONTEND_URL}/forgot-password")
        
        # Clica no link de voltar
        page.locator('[data-testid="back-to-login"]').click()
        
        # Verifica se voltou para login
        expect(page).to_have_url(f"{FRONTEND_URL}/login")
    
    def test_reset_password_page_loads(self, page: Page):
        """Testa se a página de redefinição carrega corretamente"""
        page.goto(f"{FRONTEND_URL}/reset-password")
        
        # Verifica elementos da página
        expect(page.locator('h1')).to_contain_text('Redefinir Senha')
        expect(page.locator('input[data-testid="email-input"]')).to_be_visible()
        expect(page.locator('input[data-testid="token-input"]')).to_be_visible()
        expect(page.locator('input[data-testid="new-password-input"]')).to_be_visible()
        expect(page.locator('input[data-testid="confirm-password-input"]')).to_be_visible()
    
    def test_reset_password_token_length_limit(self, page: Page):
        """Testa limite de caracteres no campo de token"""
        page.goto(f"{FRONTEND_URL}/reset-password")
        
        token_input = page.locator('input[data-testid="token-input"]')
        token_input.fill('1234567890')
        
        # Verifica se aceita no máximo 6 caracteres
        value = token_input.input_value()
        assert len(value) <= 6
    
    def test_reset_password_validation(self, page: Page):
        """Testa validação de senha mínima"""
        page.goto(f"{FRONTEND_URL}/reset-password")
        
        # Preenche com senha curta
        page.fill('input[data-testid="email-input"]', 'teste@teste.com')
        page.fill('input[data-testid="token-input"]', '123456')
        page.fill('input[data-testid="new-password-input"]', '123')
        page.fill('input[data-testid="confirm-password-input"]', '123')
        
        # Submete formulário
        page.click('button[data-testid="submit-button"]')
        
        # Verifica mensagem de erro
        error = page.locator('[data-testid="error-message"]')
        expect(error).to_be_visible(timeout=5000)

class TestUIResponsiveness:
    """Testes de responsividade da interface"""
    
    def test_mobile_viewport_login(self, page: Page):
        """Testa layout responsivo em viewport mobile"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{FRONTEND_URL}/login")
        
        # Verifica se elementos estão visíveis em mobile
        expect(page.locator('h1')).to_be_visible()
        expect(page.locator('input[name="email"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()
    
    def test_tablet_viewport_register(self, page: Page):
        """Testa layout responsivo em viewport tablet"""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(f"{FRONTEND_URL}/register")
        
        # Verifica se elementos estão visíveis em tablet
        expect(page.locator('h1')).to_be_visible()
        expect(page.locator('input[name="nome"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()
