from dotenv import load_dotenv
load_dotenv() # Carrega a chave de API do .env
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymongo import MongoClient
from pathlib import Path
import os
from openai import OpenAI

# --- Configurações ---
UPLOAD_FOLDER = Path("./uploads")
DOCUMENT_FILE = UPLOAD_FOLDER / "conhecimento_irpf.txt" # Nome do arquivo de texto
COLLECTION_NAME = "rag_documents"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small" 
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
BATCH_SIZE = 100 # Processar embeddings em lotes menores

def indexar_documentacao():
    print("--- SCRIPT DE INDEXAÇÃO RAG COM MONGODB (ARQUIVO DE TEXTO) ---")
    
    # 1. Extrair e Dividir Texto
    try:
        with open(DOCUMENT_FILE, 'r', encoding='utf-8') as f:
            text = f.read()
        print(f"✅ 1. Extraindo texto do arquivo: {DOCUMENT_FILE}")
        print(f"   -> Leitura bem-sucedida. Tamanho do texto: {len(text)} caracteres.")
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de documentação não encontrado em: {DOCUMENT_FILE}")
        print("   -> Certifique-se de que o arquivo conhecimento_irpf.txt está na pasta uploads.")
        return
    
    # Inicializa o Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    
    print(f"   -> Texto dividido em {len(chunks)} pedaços (chunks) para indexação.")
    
    # 2. Inicializar OpenAI e MongoDB
    print(f"✅ 2. Inicializando OpenAI e MongoDB...")
    
    # A chave de API é lida da variável de ambiente
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ ERRO FATAL: A variável de ambiente OPENAI_API_KEY não está configurada.")
        print("   -> Verifique se a sua OPENAI_API_KEY está configurada no arquivo .env.")
        return

    try:
        # Inicializa OpenAI client
        openai_client = OpenAI(api_key=openai_api_key)
        
        # Conecta ao MongoDB
        mongo_uri = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "taxchatdb")
        
        mongo_client = MongoClient(mongo_uri)
        db = mongo_client[db_name]
        collection = db[COLLECTION_NAME]
        
        # Limpa a coleção existente para reindexar
        collection.delete_many({})
        print(f"✅ 3. Coleção '{COLLECTION_NAME}' limpa e pronta para indexação")
        
    except Exception as e:
        print(f"❌ ERRO ao inicializar MongoDB/OpenAI: {e}")
        return

    # 4. Gerar Embeddings e Indexar em Lotes
    print(f"✅ 4. Gerando embeddings e adicionando {len(chunks)} chunks ao MongoDB...")
    
    total_inserted = 0
    
    try:
        for i in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

            print(f"   -> Processando lote {batch_num}/{total_batches} ({len(batch_chunks)} chunks)...")
            
            # Gera embeddings para o lote usando OpenAI
            embeddings_response = openai_client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=batch_chunks
            )
            
            # Prepara documentos para inserção no MongoDB
            documents_to_insert = []
            for j, chunk in enumerate(batch_chunks):
                chunk_id = i + j
                embedding = embeddings_response.data[j].embedding
                
                doc = {
                    "chunk_id": chunk_id,
                    "text": chunk,
                    "embedding": embedding,
                    "source": DOCUMENT_FILE.name,
                    "metadata": {
                        "chunk_size": len(chunk),
                        "chunk_index": chunk_id
                    }
                }
                documents_to_insert.append(doc)
            
            # Insere no MongoDB
            result = collection.insert_many(documents_to_insert)
            total_inserted += len(result.inserted_ids)
            
            print(f"   -> Lote {batch_num} adicionado com sucesso. Total inserido: {total_inserted}")

        # Cria índice para busca eficiente
        collection.create_index([("chunk_id", 1)])
        
        print(f"\n✅ INDEXAÇÃO CONCLUÍDA! Total de {total_inserted} documentos indexados no MongoDB.")
        print(f"   Banco de dados: {db_name}")
        print(f"   Coleção: {COLLECTION_NAME}")
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL durante a indexação: {e}")
        import traceback
        traceback.print_exc()
        print("   -> Verifique o limite de tokens da sua conta OpenAI ou o tamanho dos seus chunks.")
        
if __name__ == "__main__":
    indexar_documentacao()
