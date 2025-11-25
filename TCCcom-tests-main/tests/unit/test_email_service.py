"""Testes unitários para o serviço de e-mail"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Adiciona o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from email_service import send_password_reset_email, EmailDeliveryError

class TestEmailService:
    """Testes para o serviço de e-mail"""
    
    def test_send_password_reset_email_dev_mode(self, capsys):
        """Testa envio de e-mail em modo desenvolvimento (sem SendGrid)"""
        with patch('email_service.os.getenv', return_value=None):
            result = send_password_reset_email('teste@exemplo.com', '123456')
            
            assert result is True
            captured = capsys.readouterr()
            assert 'E-MAIL DE REDEFINIÇÃO DE SENHA' in captured.out
            assert '123456' in captured.out
    
    @patch('email_service.SendGridAPIClient')
    def test_send_password_reset_email_with_sendgrid(self, mock_sendgrid):
        """Testa envio de e-mail com SendGrid configurado"""
        # Mock da resposta do SendGrid
        mock_response = Mock()
        mock_response.status_code = 202
        mock_client = Mock()
        mock_client.send.return_value = mock_response
        mock_sendgrid.return_value = mock_client
        
        with patch('email_service.os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                if key == 'SENDGRID_API_KEY':
                    return 'test-api-key'
                elif key == 'SENDGRID_SENDER_EMAIL':
                    return 'noreply@test.com'
                return default
            mock_getenv.side_effect = getenv_side_effect
            
            result = send_password_reset_email('teste@exemplo.com', '123456')
            
            assert result is True
            mock_client.send.assert_called_once()
    
    @patch('email_service.SendGridAPIClient')
    def test_send_password_reset_email_sendgrid_failure(self, mock_sendgrid):
        """Testa falha ao enviar e-mail via SendGrid"""
        mock_sendgrid.side_effect = Exception('SendGrid error')
        
        with patch('email_service.os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                if key == 'SENDGRID_API_KEY':
                    return 'test-api-key'
                return default
            mock_getenv.side_effect = getenv_side_effect
            
            with pytest.raises(EmailDeliveryError):
                send_password_reset_email('teste@exemplo.com', '123456')
    
    def test_email_content_formatting(self):
        """Testa se o conteúdo do e-mail está formatado corretamente"""
        with patch('email_service.os.getenv', return_value=None):
            with patch('email_service.Mail') as mock_mail:
                send_password_reset_email('teste@exemplo.com', '987654')
                
                # Verifica se Mail foi chamado
                assert mock_mail.called
