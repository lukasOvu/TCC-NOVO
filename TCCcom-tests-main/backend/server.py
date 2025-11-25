from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os
from pathlib import Path
from bson.objectid import ObjectId # Para lidar com IDs do MongoDB
import secrets
from datetime import datetime, timedelta
from email_service import send_password_reset_email, EmailDeliveryError

# --- CONFIGURAÇÃO DO APP E BANCO DE DADOS (MongoDB) ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'uma-chave-secreta-muito-forte')
# A URI do MongoDB deve estar no seu arquivo .env ou ser configurada aqui
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "taxchatdb")
app.config["MONGO_URI"] = f"{mongo_url}/{db_name}"

# Permite que o frontend (rodando em localhost:3000) acesse o backend
CORS(app, resources={r"/*": {"origins": os.getenv('CORS_ORIGINS', 'http://localhost:3000' )}}, supports_credentials=True)

# Inicializa o MongoDB
mongo = PyMongo(app)
users_collection = mongo.db.users # Define a coleção de usuários

# --- SERVIÇO DO CHATBOT (EXISTENTE) ---
# Adiciona o diretório de trabalho atual ao caminho para encontrar os módulos locais
sys.path.insert(0, os.getcwd())
from chatbot_ir_service import ChatbotIRService

UPLOAD_FOLDER = Path("./uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

ir_service = ChatbotIRService(
    openai_api_key=os.getenv("OPENAI_API_KEY", "dummy_key"),
    upload_folder=UPLOAD_FOLDER,
    mongo_uri=os.getenv("MONGO_URL", "mongodb://localhost:27017")
)

# Dicionário para armazenar o estado da conversa
sessions = {}

# --- ROTAS DE AUTENTICAÇÃO (MongoDB) ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    # O frontend envia 'nome', 'email', 'cpf', 'senha'
    nome = data.get('nome')
    email = data.get('email')
    cpf = data.get('cpf')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'error': 'Nome, Email e Senha são obrigatórios!'}), 400

    # Verifica se o email já existe
    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'Email já cadastrado!'}), 409

    # Cria o novo usuário
    new_user = {
        'nome': nome,
        'email': email,
        'cpf': cpf, # Armazena o CPF (opcional)
        'password_hash': generate_password_hash(senha)
    }

    result = users_collection.insert_one(new_user)
    
    # Retorna o usuário criado
    user_data = {
        'id': str(result.inserted_id),
        'nome': nome,
        'email': email
    }

    return jsonify({'message': 'Usuário cadastrado com sucesso!', 'user': user_data}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    user = users_collection.find_one({'email': email})

    if not user or not check_password_hash(user['password_hash'], senha):
        return jsonify({'error': 'Email ou senha inválidos!'}), 401

    # Usa o ID do MongoDB como ID de sessão
    session['user_id'] = str(user['_id'])
    
    # Retorna dados do usuário
    user_data = {
        'id': str(user['_id']),
        'nome': user['nome'],
        'email': user['email']
    }
    
    return jsonify({'message': 'Login realizado com sucesso!', 'user': user_data}), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout realizado com sucesso!'}), 200

@app.route('/api/check_session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        if user:
            return jsonify({'logged_in': True, 'username': user['nome']}), 200
    return jsonify({'logged_in': False}), 401

# --- ROTAS DE REDEFINIÇÃO DE SENHA ---
@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Solicita redefinição de senha e envia token por e-mail"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'E-mail é obrigatório'}), 400
    
    # Verifica se o usuário existe
    user = users_collection.find_one({'email': email})
    
    if not user:
        # Por segurança, não revelamos se o e-mail existe ou não
        return jsonify({'message': 'Se o e-mail existir, você receberá um código de redefinição.'}), 200
    
    # Gera token de 6 dígitos
    reset_token = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    # Define expiração para 15 minutos
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Salva o token no banco de dados
    users_collection.update_one(
        {'_id': user['_id']},
        {
            '$set': {
                'reset_token': reset_token,
                'reset_token_expires': expires_at
            }
        }
    )
    
    # Envia e-mail com o token
    try:
        send_password_reset_email(email, reset_token)
        return jsonify({'message': 'Código de redefinição enviado por e-mail!'}), 200
    except EmailDeliveryError as e:
        return jsonify({'error': 'Erro ao enviar e-mail. Tente novamente.'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Redefine a senha usando o token recebido"""
    data = request.get_json()
    email = data.get('email')
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not email or not token or not new_password:
        return jsonify({'error': 'E-mail, token e nova senha são obrigatórios'}), 400
    
    # Valida tamanho mínimo da senha
    if len(new_password) < 6:
        return jsonify({'error': 'A senha deve ter no mínimo 6 caracteres'}), 400
    
    # Busca o usuário
    user = users_collection.find_one({'email': email})
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    # Verifica se o token existe
    if 'reset_token' not in user or 'reset_token_expires' not in user:
        return jsonify({'error': 'Token inválido ou expirado'}), 400
    
    # Verifica se o token está correto
    if user['reset_token'] != token:
        return jsonify({'error': 'Token inválido'}), 400
    
    # Verifica se o token não expirou
    if datetime.utcnow() > user['reset_token_expires']:
        return jsonify({'error': 'Token expirado. Solicite um novo código.'}), 400
    
    # Atualiza a senha e remove o token
    users_collection.update_one(
        {'_id': user['_id']},
        {
            '$set': {
                'password_hash': generate_password_hash(new_password)
            },
            '$unset': {
                'reset_token': '',
                'reset_token_expires': ''
            }
        }
    )
    
    return jsonify({'message': 'Senha redefinida com sucesso!'}), 200

# --- ROTAS DO CHATBOT (EXISTENTES) ---
@app.route('/')
def index():
    return jsonify({"message": "TaxXat Backend is running!", "status": "ok"})

@app.route('/api/chat', methods=['POST'])
async def chat():
    if 'user_id' not in session:
        return jsonify({"response": "Acesso não autorizado. Por favor, faça o login."}), 401

    data = request.json
    message = data.get('message', '')
    session_id = session['user_id'] # Usa o ID do usuário como ID da sessão do chatbot

    if session_id not in sessions:
        sessions[session_id] = {
            "state": ir_service.STATE_IDLE,
            "documents": [],
            "analysis_results": None
        }

    current_session = sessions[session_id]
    response_text = ""

    if ir_service.detect_ir_calculation_intent(message):
        response_text = ir_service.get_welcome_message()
        current_session["state"] = ir_service.STATE_REQUESTING_DOCS
    elif current_session["state"] == ir_service.STATE_REQUESTING_DOCS and ir_service.check_user_ready(message):
        response_text = "✅ Documentos recebidos. Iniciando a análise..."
        current_session["state"] = ir_service.STATE_ANALYZING_DOCS
        response_text += "\n\nPor favor, me pergunte algo sobre Imposto de Renda para testar o RAG."
    elif current_session["state"] == ir_service.STATE_ANALYZING_DOCS:
        response_text = ir_service._get_rag_response(message)
    else:
        response_text = ir_service._get_rag_response(message)

    return jsonify({"response": response_text, "session_state": current_session["state"]})

@app.route('/api/upload', methods=['POST'])
def upload_document():
    if 'user_id' not in session:
        return jsonify({"message": "Acesso não autorizado."}), 401

    if 'file' not in request.files:
        return jsonify({"message": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "Nenhum arquivo selecionado"}), 400
    
    if file:
        filename = file.filename
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        return jsonify({"message": "Upload realizado com sucesso", "filepath": str(filepath)}), 200

@app.route('/api/analyze', methods=['POST'])
async def analyze_documents():
    if 'user_id' not in session:
        return jsonify({"message": "Acesso não autorizado."}), 401

    data = request.json
    files_to_analyze = data.get('files', [])
    session_id = session['user_id']
    
    if session_id not in sessions:
        sessions[session_id] = {"state": ir_service.STATE_IDLE, "documents": [], "analysis_results": None}
        
    current_session = sessions[session_id]
    analysis_results = []
    
    for file_path in files_to_analyze:
        result = await ir_service.analyze_document(file_path, Path(file_path).name)
        analysis_results.append(result)
        
    aggregated_data = ir_service.aggregate_document_data(analysis_results)
    calculation = ir_service.calculate_ir(aggregated_data)
    final_message = ir_service.format_result_message(calculation, aggregated_data)
    
    current_session["analysis_results"] = calculation
    current_session["state"] = ir_service.STATE_COMPLETE
    
    return jsonify({"message": final_message, "analysis": analysis_results, "calculation": calculation})

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    print("Servidor Flask IRPF iniciado. Rodando em http://0.0.0.0:8001" )
    app.run(host='0.0.0.0', port=8001, debug=True)
