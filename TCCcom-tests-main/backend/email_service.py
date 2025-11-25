from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

class EmailDeliveryError(Exception):
    pass

def send_password_reset_email(to_email: str, reset_token: str):
    """
    Envia e-mail com token de redefinição de senha
    
    Args:
        to_email: E-mail do destinatário
        reset_token: Token de redefinição de 6 dígitos
    """
    sender_email = os.getenv('SENDGRID_SENDER_EMAIL', 'noreply@taxchat.com')
    subject = "Redefinição de Senha - TAXXAT"
    
    html_content = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .token {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    text-align: center;
                    padding: 20px;
                    background-color: #f0f4ff;
                    border-radius: 8px;
                    margin: 20px 0;
                    letter-spacing: 5px;
                }}
                .warning {{
                    color: #d32f2f;
                    font-size: 14px;
                    text-align: center;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Redefinição de Senha</h1>
                </div>
                <div class="content">
                    <p>Olá,</p>
                    <p>Você solicitou a redefinição de senha da sua conta TAXXAT.</p>
                    <p>Use o código abaixo para redefinir sua senha:</p>
                    
                    <div class="token">{reset_token}</div>
                    
                    <p>Digite este código na página de redefinição de senha.</p>
                    
                    <div class="warning">
                        ⚠️ Este código expira em 15 minutos.
                    </div>
                    
                    <p style="margin-top: 30px;">Se você não solicitou esta redefinição, ignore este e-mail.</p>
                </div>
                <div class="footer">
                    <p>© 2024 TAXXAT - Assistente Inteligente de Imposto de Renda</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    message = Mail(
        from_email=sender_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        if not sendgrid_api_key:
            # Para desenvolvimento: apenas loga o token
            print(f"\n{'='*60}")
            print(f"📧 E-MAIL DE REDEFINIÇÃO DE SENHA (DEV MODE)")
            print(f"Para: {to_email}")
            print(f"Token: {reset_token}")
            print(f"Expira em: 15 minutos")
            print(f"{'='*60}\n")
            return True
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")
        # Em desenvolvimento, ainda retorna True para não bloquear o fluxo
        if not os.getenv('SENDGRID_API_KEY'):
            return True
        raise EmailDeliveryError(f"Falha ao enviar e-mail: {str(e)}")
