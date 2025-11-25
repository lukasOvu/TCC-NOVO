"""Configuração do Playwright para testes de GUI"""
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    """Inicia o navegador para os testes"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    """Cria uma nova página para cada teste"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    page.close()
    context.close()
