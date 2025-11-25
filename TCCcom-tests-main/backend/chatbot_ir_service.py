from openai import OpenAI
from pathlib import Path
import json
import re
import os
from typing import Dict, List, Optional
import numpy as np
from pymongo import MongoClient

# --- SOLUÇÃO FINAL E ABSOLUTA: NOVO NOME DE ARQUIVO ---
# O arquivo foi renomeado para irpf_calculadora.py
from irpf_calculadora import CalculadoraIRPF


# Importações originais (mantidas para OCR)
from PIL import Image
import pytesseract
from pdf2image import convert_from_path 

# --- Configurações RAG com MongoDB ---
COLLECTION_NAME = "rag_documents"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small" 

class ChatbotIRService:
    """Gerencia o fluxo de cálculo de IR através do chatbot com OCR e RAG."""
    
    # Estados da conversa
    STATE_IDLE = "idle"
    STATE_REQUESTING_DOCS = "requesting_documents"
    STATE_WAITING_DOCS = "waiting_documents"
    STATE_ANALYZING_DOCS = "analyzing_documents"
    STATE_CALCULATING = "calculating"
    STATE_COMPLETE = "complete"
    
    # Tipos de documentos necessários
    REQUIRED_DOCS = {
        "informe_rendimentos": "Informe de Rendimentos",
        "despesas_medicas": "Comprovantes de Despesas Médicas",
        "despesas_educacao": "Comprovantes de Despesas com Educação",
        "outros_recibos": "Outros Recibos e Comprovantes"
    }
    
    def __init__(self, openai_api_key: str, upload_folder: Path, mongo_uri: str = None):
        """Inicializa o serviço com a chave da API OpenAI, RAG e Calculadora."""
        
        chave_api = os.getenv("OPENAI_API_KEY")
        
        if not chave_api:
            chave_api = openai_api_key
            
        if not chave_api or chave_api == "dummy_key":
            raise ValueError("OPENAI_API_KEY não encontrada. Verifique o arquivo .env e o server.py.")
            
        self.client = OpenAI(api_key=chave_api)
        self.model = "gpt-4o"
        self.upload_folder = upload_folder
        self.calculadora = CalculadoraIRPF()
        
        # MongoDB connection
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "taxchatdb")
        
        self._initialize_rag()
        
    def _initialize_rag(self):
        """Inicializa o MongoDB para RAG."""
        try:
            # Conecta ao MongoDB
            self.mongo_client = MongoClient(self.mongo_uri)
            self.db = self.mongo_client[self.db_name]
            self.rag_collection = self.db[COLLECTION_NAME]
            
            # Cria índice para busca eficiente
            self.rag_collection.create_index([("chunk_id", 1)])
            
            doc_count = self.rag_collection.count_documents({})
            print(f"✅ RAG Inicializado com MongoDB: {doc_count} documentos indexados.")
            
        except Exception as e:
            self.rag_collection = None
            self.mongo_client = None
            print(f"❌ ERRO ao inicializar RAG: {e}. O chatbot funcionará sem o conhecimento customizado.")


    def detect_ir_calculation_intent(self, message: str) -> bool:
        """Detecta se o usuário quer calcular o IR ou fazer perguntas sobre IR."""
        keywords = [
            "calcul", "imposto", "ir", "declaração", "declarar",
            "quanto", "pagar", "devo", "restituição", "restituir",
            "calcule meu ir", "fazer minha declaração", "meu imposto",
            "alíquota", "dedução", "mei", "renda fixa" 
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
    
    def get_welcome_message(self) -> str:
        """Retorna mensagem de boas-vindas e solicita documentos."""
        return """🎯 **Perfeito! Vou ajudar você a calcular seu Imposto de Renda.**
        
Para fazer um cálculo preciso, vou precisar que você me envie os seguintes documentos:
        
📋 **Documentos Necessários:**
        
1️⃣ **Informe de Rendimentos** - Fornecido pela sua empresa (salários, 13º, etc)
2️⃣ **Comprovantes de Despesas Médicas** - Recibos de consultas, exames, planos de saúde
3️⃣ **Comprovantes de Despesas com Educação** - Mensalidades escolares, cursos
4️⃣ **Outros Comprovantes** - Pensão alimentícia, doações, previdência privada
        
📤 **Como enviar:**
1. Vá na aba "Documentos" 
2. Faça o upload de cada documento (PDF, JPG ou PNG)
3. Volte aqui e digite: "documentos enviados" ou "pronto"
        
💡 **Dica:** Quanto mais completos seus documentos, mais preciso será o cálculo!
        
Já enviou os documentos? Digite "pronto" ou "documentos enviados" para eu começar a análise! ✅"""
    
    def check_user_ready(self, message: str) -> bool:
        """Verifica se o usuário confirmou que enviou os documentos"""
        ready_keywords = [
            "pronto", "enviado", "enviei", "ok", "sim", "feito",
            "documentos enviados", "já enviei", "upload feito"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in ready_keywords)
    
    # --- FUNÇÕES DE EXTRAÇÃO DE TEXTO (OCR) ---
    def extract_text_from_image(self, image_path: str) -> str:
        """Extrai texto de imagem usando Tesseract OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(
                image, 
                lang='por+eng',
                config='--psm 6'
            )
            return text.strip()
        except Exception as e:
            print(f"Erro ao extrair texto da imagem {image_path}: {str(e)}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrai texto de PDF usando pdf2image + Tesseract OCR (Fallback)"""
        try:
            images = convert_from_path(
                pdf_path,
                dpi=300,
                first_page=1,
                last_page=10
            )
            
            all_text = []
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(
                    image,
                    lang='por+eng',
                    config='--psm 6'
                )
                all_text.append(text.strip())
            
            return "\n\n--- NOVA PÁGINA ---\n\n".join(all_text)
        except Exception as e:
            print(f"Erro ao extrair texto do PDF {pdf_path}: {str(e)}")
            return ""
    # --- FIM FUNÇÕES DE EXTRAÇÃO DE TEXTO (OCR) ---
    
    async def analyze_document(self, filepath: str, filename: str) -> Dict:
        """Analisa um documento usando OCR + OpenAI"""
        try:
            print(f"🔍 Analisando documento: {filename}")
            
            extracted_text = ""
            
            if filepath.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"  📷 Tipo: Imagem - Aplicando OCR...")
                extracted_text = self.extract_text_from_image(filepath)
            elif filepath.lower().endswith('.pdf'):
                print(f"  📄 Tipo: PDF - Convertendo e aplicando OCR...")
                extracted_text = self.extract_text_from_pdf(filepath) 
            elif filepath.lower().endswith('.txt'):
                print(f"  📝 Tipo: Texto - Lendo conteúdo...")
                with open(filepath, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            else:
                return {
                    "filename": filename,
                    "status": "error",
                    "error": f"Tipo de arquivo não suportado: {filename}"
                }
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                return {
                    "filename": filename,
                    "status": "error",
                    "error": "Não foi possível extrair texto do documento. Verifique a qualidade da imagem/PDF."
                }
            
            print(f"  ✅ Texto extraído: {len(extracted_text)} caracteres")
            print(f"  🤖 Analisando com OpenAI GPT-4o...")
            
            # Limita o texto para evitar estouro de tokens
            analysis = await self._analyze_text_with_openai(extracted_text[:30000], filename)
            
            return {
                "filename": filename,
                "type": Path(filepath).suffix.lower(),
                "status": "success",
                "extracted_text": extracted_text[:500],
                "extracted_data": analysis,
                "raw_analysis": str(analysis)
            }
            
        except Exception as e:
            print(f"❌ Erro ao analisar {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "filename": filename,
                "status": "error",
                "error": str(e)
            }
    
    async def _analyze_text_with_openai(self, text: str, filename: str) -> Dict:
        """Analisa texto extraído usando OpenAI GPT-4o"""
        try:
            prompt = f"""Você é um especialista em análise de documentos fiscais brasileiros para Imposto de Renda.

Analise o seguinte texto extraído de um documento ({filename}) e extraia TODAS as informações relevantes para cálculo de IR.

TEXTO DO DOCUMENTO:
{text}

Por favor, retorne APENAS um objeto JSON válido (sem markdown, sem texto adicional) com a seguinte estrutura:

{{
  "tipo_documento": "informe_rendimentos | despesa_medica | despesa_educacao | outro",
  "rendimentos": {{
    "salario_mensal": 0.0,
    "decimo_terceiro": 0.0,
    "ferias": 0.0,
    "bonus": 0.0,
    "total_anual": 0.0,
    "imposto_retido_fonte": 0.0 
  }},
  "despesas_medicas": {{
    "consultas": 0.0,
    "exames": 0.0,
    "plano_saude": 0.0,
    "total": 0.0
  }},
  "despesas_educacao": {{
    "mensalidades": 0.0,
    "material": 0.0,
    "total": 0.0
  }},
  "outras_deducoes": {{
    "inss": 0.0,
    "previdencia_privada": 0.0,
    "pensao_alimenticia": 0.0,
    "doacoes": 0.0,
    "total": 0.0
  }},
  "informacoes_pessoais": {{
    "nome": "",
    "cpf": "",
    "periodo": "",
    "num_dependentes": 0 
  }},
  "observacoes": "Qualquer observação importante"
}}

IMPORTANTE: 
- Extraia TODOS os valores monetários que encontrar
- Se não encontrar um valor, deixe como 0.0
- Seja preciso com os números
- Retorne APENAS o JSON, sem texto adicional"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em análise de documentos fiscais. Sempre retorne apenas JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000 
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            analysis_text = analysis_text.replace('```json', '').replace('```', '').strip()
            
            analysis_data = json.loads(analysis_text)
            
            print(f"  ✅ Análise OpenAI concluída: {analysis_data.get('tipo_documento', 'desconhecido')}")
            
            return analysis_data
            
        except json.JSONDecodeError as e:
            print(f"  ⚠️ Erro ao parsear JSON da resposta OpenAI: {str(e)}")
            print(f"  Resposta recebida: {analysis_text[:200]}...")
            return self._extract_values_manually(text)
        except Exception as e:
            print(f"  ❌ Erro na análise OpenAI: {str(e)}")
            return self._extract_values_manually(text)
    
    def _extract_values_manually(self, text: str) -> Dict:
        """Extrai valores manualmente do texto como fallback"""
        data = {
            "tipo_documento": "outro",
            "rendimentos": {"total_anual": 0.0, "imposto_retido_fonte": 0.0},
            "despesas_medicas": {"total": 0.0},
            "despesas_educacao": {"total": 0.0},
            "outras_deducoes": {"total": 0.0},
            "informacoes_pessoais": {"num_dependentes": 0},
            "observacoes": "Análise automática com extração manual"
        }
        
        money_pattern = r'R?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)'
        values = re.findall(money_pattern, text)
        
        if values:
            data['valores_encontrados'] = values
        
        cpf_pattern = r'\d{3}\.\d{3}\.\d{3}-\d{2}'
        cpf = re.search(cpf_pattern, text)
        if cpf:
            data['informacoes_pessoais']['cpf'] = cpf.group()
        
        return data
    
    def aggregate_document_data(self, analyses: List[Dict]) -> Dict:
        """Agrega dados de múltiplos documentos"""
        aggregated = {
            "rendimentos_tributaveis": 0.0,
            "imposto_retido_fonte": 0.0, 
            "despesas_medicas": 0.0,
            "despesas_educacao": 0.0,
            "outras_deducoes": 0.0,
            "num_dependentes": 0, 
            "erros": [],
            "avisos": [],
            "documentos_analisados": 0
        }
        
        for analysis in analyses:
            if analysis.get("status") == "error":
                aggregated["erros"].append(f"❌ {analysis['filename']}: {analysis.get('error', 'Erro desconhecido')}")
                continue
            
            aggregated["documentos_analisados"] += 1
            extracted = analysis.get("extracted_data", {})
            
            # Extrair rendimentos e imposto retido
            if "rendimentos" in extracted:
                rend = extracted["rendimentos"]
                total = rend.get("total_anual", 0.0)
                if total == 0:
                    total = sum([
                        rend.get("salario_mensal", 0.0) * 12,
                        rend.get("decimo_terceiro", 0.0),
                        rend.get("ferias", 0.0),
                        rend.get("bonus", 0.0)
                    ])
                aggregated["rendimentos_tributaveis"] += total
                aggregated["imposto_retido_fonte"] += rend.get("imposto_retido_fonte", 0.0)
            
            # Extrair despesas médicas
            if "despesas_medicas" in extracted:
                desp_med = extracted["despesas_medicas"]
                total = desp_med.get("total", 0.0)
                if total == 0:
                    total = sum([
                        desp_med.get("consultas", 0.0),
                        desp_med.get("exames", 0.0),
                        desp_med.get("plano_saude", 0.0)
                    ])
                aggregated["despesas_medicas"] += total
            
            # Extrair despesas educação
            if "despesas_educacao" in extracted:
                desp_edu = extracted["despesas_educacao"]
                total = desp_edu.get("total", 0.0)
                if total == 0:
                    total = sum([
                        desp_edu.get("mensalidades", 0.0),
                        desp_edu.get("material", 0.0)
                    ])
                aggregated["despesas_educacao"] += total
            
            # Outras deduções
            if "outras_deducoes" in extracted:
                outras = extracted["outras_deducoes"]
                total = outras.get("total", 0.0)
                if total == 0:
                    total = sum([
                        outras.get("inss", 0.0),
                        outras.get("previdencia_privada", 0.0),
                        outras.get("pensao_alimenticia", 0.0),
                        outras.get("doacoes", 0.0)
                    ])
                aggregated["outras_deducoes"] += total

            # Dependentes
            if "informacoes_pessoais" in extracted:
                aggregated["num_dependentes"] = max(aggregated["num_dependentes"], extracted["informacoes_pessoais"].get("num_dependentes", 0))
        
        # Validações
        if aggregated["rendimentos_tributaveis"] == 0:
            aggregated["avisos"].append("⚠️ Não foi possível identificar rendimentos nos documentos. O cálculo será impreciso.")
        
        if aggregated["documentos_analisados"] == 0:
            aggregated["avisos"].append("⚠️ Não foi possível analisar nenhum documento com sucesso.")
        
        print(f"\n📊 AGREGAÇÃO FINAL:")
        print(f"  Rendimentos Tributáveis: R$ {aggregated['rendimentos_tributaveis']:,.2f}")
        print(f"  IR Retido na Fonte: R$ {aggregated['imposto_retido_fonte']:,.2f}")
        
        return aggregated
    
    def calculate_ir(self, data: Dict) -> Dict:
        """Calcula o Imposto de Renda baseado nos dados extraídos usando a CalculadoraIRPF."""
        
        rendimentos_tributaveis = data.get("rendimentos_tributaveis", 0)
        imposto_retido_fonte = data.get("imposto_retido_fonte", 0)
        despesas_medicas = data.get("despesas_medicas", 0)
        despesas_educacao = data.get("despesas_educacao", 0)
        outras_deducoes = data.get("outras_deducoes", 0)
        num_dependentes = data.get("num_dependentes", 0)
        
        despesas_dedutiveis = despesas_medicas + outras_deducoes
        
        try:
            calculo_pf = self.calculadora.calcular_irpf_anual(
                rendimentos_tributaveis=rendimentos_tributaveis,
                despesas_dedutiveis=despesas_dedutiveis,
                num_dependentes=num_dependentes,
                despesas_instrucao=despesas_educacao,
                imposto_retido_fonte=imposto_retido_fonte
            )
            
            calculo_pf["rendimentos_tributaveis"] = round(rendimentos_tributaveis, 2)
            calculo_pf["despesas_medicas"] = round(despesas_medicas, 2)
            calculo_pf["despesas_educacao"] = round(despesas_educacao, 2)
            calculo_pf["outras_deducoes"] = round(outras_deducoes, 2)
            calculo_pf["num_dependentes"] = num_dependentes
            
            return calculo_pf
        
        except Exception as e:
            print(f"ERRO NO CÁLCULO: {e}")
            return {
                "status_final": "error",
                "error": f"Erro no cálculo: {str(e)}"
            }

    def format_result_message(self, calculation: Dict, aggregated_data: Dict) -> str:
        """Formata mensagem final com resultado do cálculo e RAG."""
        
        if calculation.get("status_final") == "error":
            return f"❌ **Erro no Cálculo**\n\n{calculation.get('error')}\n\nPor favor, verifique seus documentos e tente novamente."
        
        msg = "✅ **CÁLCULO DE IMPOSTO DE RENDA CONCLUÍDO!**\n\n"
        msg += "🤖 **Análise realizada com OCR, IA e Regras Fiscais**\n\n"
        msg += "═══════════════════════════════════════\n\n"
        
        if aggregated_data.get("erros"):
            msg += "⚠️ **ERROS ENCONTRADOS NA EXTRAÇÃO:**\n"
            for erro in aggregated_data["erros"]:
                msg += f"{erro}\n"
            msg += "\n"
        
        if aggregated_data.get("avisos"):
            msg += "⚠️ **AVISOS:**\n"
            for aviso in aggregated_data["avisos"]:
                msg += f"{aviso}\n"
            msg += "\n"
        
        msg += f"📄 **Documentos analisados:** {aggregated_data.get('documentos_analisados', 0)}\n\n"
        
        msg += "📊 **RESUMO DOS SEUS DADOS:**\n\n"
        msg += f"💰 **Rendimentos Tributáveis:** R$ {calculation['rendimentos_tributaveis']:,.2f}\n"
        msg += f"➖ **IR Retido na Fonte:** R$ {calculation['imposto_retido_fonte']:,.2f}\n"
        msg += f"👶 **Dependentes:** {calculation['num_dependentes']}\n"
        msg += f"🏥 **Despesas Médicas:** R$ {calculation['despesas_medicas']:,.2f}\n"
        msg += f"🎓 **Despesas com Educação:** R$ {calculation['despesas_educacao']:,.2f}\n\n"
        
        msg += "📈 **RESULTADO DO CÁLCULO IRPF (Pessoa Física Anual):**\n"
        msg += f"   • **Opção Mais Vantajosa:** {calculation['melhor_opcao']}\n"
        msg += f"   • **Base de Cálculo:** R$ {calculation['base_calculo_final']:,.2f}\n"
        msg += f"   • **Alíquota Efetiva:** {calculation['aliquota_final']:.1f}%\n"
        msg += f"   • **Imposto Devido Total:** R$ {calculation['imposto_devido_final']:,.2f}\n\n"
        
        msg += "═══════════════════════════════════════\n\n"
        
        if calculation['status_final'] == "Restituição":
             msg += f"🎉 **RESTITUIÇÃO A RECEBER:** R$ {calculation['valor_final']:,.2f}\n\n"
        else:
             msg += f"💵 **IMPOSTO A PAGAR:** R$ {calculation['valor_final']:,.2f}\n\n"
             
        # 5. Adiciona o Conhecimento do RAG
        rag_info = self._get_rag_response(f"O que é {calculation['status_final']} no IRPF e quais são as regras de {calculation['melhor_opcao']}?")
        if rag_info:
            msg += f"📚 **CONHECIMENTO EXTRAÍDO DA SUA DOCUMENTAÇÃO (RAG):**\n"
            msg += f"{rag_info}\n\n"
        
        msg += "⚠️ **IMPORTANTE:**\n"
        msg += "• Esta é uma simulação baseada nos documentos enviados.\n"
        msg += "• Consulte um contador para cálculo oficial e declaração.\n"
        
        return msg

    def _get_rag_response(self, query: str) -> str:
        """Busca informações no MongoDB e gera uma resposta contextualizada com a OpenAI."""
        if not self.rag_collection:
            return "O sistema RAG não está ativo. Não foi possível consultar sua documentação customizada. **Atenção: Rode o rag_indexer.py para ativar o RAG!**"
        
        try:
            # 1. Gera embedding da query usando OpenAI
            query_embedding_response = self.client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=query
            )
            query_embedding = query_embedding_response.data[0].embedding
            
            # 2. Busca os documentos mais relevantes usando similaridade de cosseno
            all_docs = list(self.rag_collection.find({}))
            
            if not all_docs:
                return "Não foram encontrados documentos na sua base de conhecimento customizada. Execute o rag_indexer.py primeiro."
            
            # Calcula similaridade de cosseno para cada documento
            similarities = []
            for doc in all_docs:
                if 'embedding' in doc:
                    doc_embedding = doc['embedding']
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    similarities.append((similarity, doc))
            
            # Ordena por similaridade (maior primeiro) e pega os top 3
            similarities.sort(reverse=True, key=lambda x: x[0])
            top_docs = similarities[:3]
            
            # 3. Constrói o contexto com os documentos encontrados
            context = ""
            sources = []
            for similarity, doc in top_docs:
                context += f"--- Documento (Chunk {doc.get('chunk_id')}):\n{doc.get('text')}\n---\n"
                sources.append(f"Chunk {doc.get('chunk_id')} do arquivo '{doc.get('source')}'")
            
            if not context:
                return "Não foram encontrados documentos relevantes na sua base de conhecimento customizada."

            # 4. Gera a resposta contextualizada com o GPT-4o
            rag_prompt = f"""
            Você é um assistente especializado em Imposto de Renda. Sua resposta deve ser baseada EXCLUSIVAMENTE no CONTEXTO fornecido.

            CONTEXTO (Documentação de IRPF do Usuário):
            {context}

            PERGUNTA DO USUÁRIO: {query}

            Instruções:
            1. Responda à pergunta do usuário de forma concisa, utilizando apenas as informações do CONTEXTO.
            2. Mencione as fontes (Chunk X) de onde a informação foi retirada.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente de IRPF que responde com base em documentos fornecidos (RAG)."},
                    {"role": "user", "content": rag_prompt}
                ],
                temperature=0.0,
                max_tokens=500
            )
            
            rag_response = response.choices[0].message.content.strip()
            
            return rag_response
            
        except Exception as e:
            print(f"❌ ERRO NO RAG: {e}")
            import traceback
            traceback.print_exc()
            return "Ocorreu um erro ao consultar a base de conhecimento customizada."
    
    def _cosine_similarity(self, vec1, vec2):
        """Calcula a similaridade de cosseno entre dois vetores."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Fim do chatbot_ir_service.py
