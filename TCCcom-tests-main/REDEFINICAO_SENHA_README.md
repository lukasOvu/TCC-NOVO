# Sistema de Redefinição de Senha - TAXXAT

## ✅ Funcionalidade Implementada

O sistema de redefinição de senha foi implementado com sucesso! Agora os usuários podem recuperar suas contas caso esqueçam a senha.

## 🔧 Como Funciona

1. **Usuário esquece a senha** → Clica em "Esqueceu sua senha?" na página de login
2. **Digite o e-mail** → Sistema gera um código de 6 dígitos
3. **Código enviado por e-mail** → Válido por 15 minutos
4. **Digite o código** → Junto com a nova senha
5. **Senha redefinida** → Usuário pode fazer login normalmente

## 📧 Configuração do SendGrid (Envio de E-mails)

### Modo Atual: DESENVOLVIMENTO
Atualmente, o sistema está em **modo desenvolvimento**. Quando um usuário solicita redefinição de senha:
- O código é gerado e salvo no banco de dados ✅
- O código aparece nos **logs do backend** (não é enviado por e-mail)
- Você pode ver o código em `/var/log/supervisor/backend.out.log`

### Como Configurar o SendGrid para Produção

#### Passo 1: Criar Conta no SendGrid
1. Acesse: https://signup.sendgrid.com/
2. Crie uma conta gratuita (permite enviar até 100 e-mails por dia)
3. Verifique seu e-mail

#### Passo 2: Criar API Key
1. Faça login no SendGrid: https://app.sendgrid.com/
2. Vá em **Settings** → **API Keys**
3. Clique em **Create API Key**
4. Nome: `TAXXAT-Password-Reset`
5. Permissões: Selecione **Full Access** (ou no mínimo **Mail Send**)
6. Clique em **Create & View**
7. **COPIE A API KEY** (ela só será mostrada uma vez!)

#### Passo 3: Verificar E-mail de Remetente
1. No SendGrid, vá em **Settings** → **Sender Authentication**
2. Clique em **Verify a Single Sender**
3. Preencha os dados:
   - **From Name:** TAXXAT
   - **From Email Address:** noreply@seudominio.com (use um e-mail válido)
   - Preencha os outros campos
4. Clique em **Create**
5. Verifique o e-mail de confirmação enviado pelo SendGrid

#### Passo 4: Adicionar as Credenciais no Sistema
1. Abra o arquivo `/app/backend/.env`
2. Adicione as seguintes linhas (descomente e preencha):

```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_SENDER_EMAIL=noreply@seudominio.com
```

3. Substitua:
   - `SG.xxx...` pela sua API key copiada no Passo 2
   - `noreply@seudominio.com` pelo e-mail verificado no Passo 3

#### Passo 5: Reiniciar o Backend
```bash
sudo supervisorctl restart backend
```

#### Passo 6: Testar
Teste o fluxo de redefinição de senha. Agora os e-mails serão enviados de verdade!

## 🧪 Como Testar (Modo Desenvolvimento)

### Teste via API (curl)

#### 1. Registrar um usuário:
```bash
curl -X POST "https://senha-redefinir.preview.emergentagent.com/api/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{"nome":"Teste User","email":"teste@example.com","senha":"senha123"}'
```

#### 2. Solicitar redefinição de senha:
```bash
curl -X POST "https://senha-redefinir.preview.emergentagent.com/api/auth/forgot-password" \\
  -H "Content-Type: application/json" \\
  -d '{"email":"teste@example.com"}'
```

#### 3. Verificar o código nos logs:
```bash
tail -n 50 /var/log/supervisor/backend.out.log | grep "Token:"
```

Ou buscar no MongoDB:
```bash
mongosh "mongodb://localhost:27017/test_database" \\
  --eval "db.users.findOne({email: 'teste@example.com'})"
```

#### 4. Redefinir senha com o código:
```bash
curl -X POST "https://senha-redefinir.preview.emergentagent.com/api/auth/reset-password" \\
  -H "Content-Type: application/json" \\
  -d '{"email":"teste@example.com","token":"123456","new_password":"novaSenha123"}'
```

#### 5. Testar login com nova senha:
```bash
curl -X POST "https://senha-redefinir.preview.emergentagent.com/api/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{"email":"teste@example.com","senha":"novaSenha123"}'
```

### Teste via Interface

1. Acesse: https://senha-redefinir.preview.emergentagent.com/login
2. Clique em **"Esqueceu sua senha?"**
3. Digite seu e-mail
4. Veja o código nos logs do backend
5. Acesse: https://senha-redefinir.preview.emergentagent.com/reset-password
6. Digite e-mail, código e nova senha
7. Faça login com a nova senha

## 🏗️ Arquitetura Implementada

### Backend (Flask)
- **`/api/auth/forgot-password`** - Gera e salva token, envia e-mail
- **`/api/auth/reset-password`** - Valida token e atualiza senha
- **`email_service.py`** - Serviço de envio de e-mails via SendGrid

### Frontend (React)
- **`/forgot-password`** - Página para solicitar redefinição
- **`/reset-password`** - Página para redefinir senha
- Link "Esqueceu sua senha?" na página de login

### Banco de Dados (MongoDB)
Novos campos na collection `users`:
- `reset_token` - Código de 6 dígitos
- `reset_token_expires` - Data/hora de expiração (15 minutos)

## 🔒 Segurança

✅ Token de 6 dígitos (1.000.000 combinações)
✅ Expiração de 15 minutos
✅ Token descartado após uso
✅ Senhas hasheadas com `werkzeug.security`
✅ Por segurança, não revelamos se o e-mail existe

## 📱 Páginas Criadas

1. **Página "Esqueceu a Senha"** (`/forgot-password`)
   - Usuário digita e-mail
   - Recebe código por e-mail

2. **Página "Redefinir Senha"** (`/reset-password`)
   - Usuário digita e-mail, código e nova senha
   - Senha é atualizada

## 🎨 Design

As páginas seguem o mesmo padrão visual do resto da aplicação:
- Layout dividido (formulário + banner)
- Cores roxo/azul
- Design responsivo
- Mensagens de erro/sucesso

## 💡 Dicas

1. **Limite de Envios:** O SendGrid gratuito permite 100 e-mails/dia
2. **Produção:** Configure um domínio próprio para melhor deliverability
3. **Logs:** Sempre monitore os logs do backend para debug
4. **Segurança:** Não compartilhe sua API key do SendGrid

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs: `tail -f /var/log/supervisor/backend.err.log`
2. Verifique se o backend está rodando: `sudo supervisorctl status backend`
3. Teste as APIs diretamente com curl
4. Verifique se as credenciais do SendGrid estão corretas

---

**Desenvolvido para TAXXAT** 🚀
