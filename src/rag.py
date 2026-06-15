import chromadb
from chromadb.utils import embedding_functions
from converter import extrair_texto_pdf
from chunking import dividir_texto_em_chunks
from pathlib import Path
# 1. Encontra a raiz do projeto (voltando uma pasta a partir de 'src')
RAIZ_PROJETO = Path(__file__).resolve().parent.parent

# 2. Define e cria a pasta 'db' na raiz (se ela ainda não existir)
PASTA_DB = RAIZ_PROJETO / "db"
PASTA_DB.mkdir(exist_ok=True)

# 3. Define o caminho final do arquivo rag
DB_PATH = PASTA_DB / "rag_db"
DB_PATH.mkdir(exist_ok=True)
# Configura o banco vetorial e o modelo de embeddings (gratuito e local)
chroma_client = chromadb.PersistentClient(path=DB_PATH)
modelo_embedding = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

colecao = chroma_client.get_or_create_collection(
    name="materiais_academicos",
    embedding_function=modelo_embedding
)

def indexar_documento(caminho_pdf: str, doc_id: str):
    """
    Pipeline completo: Converte, divide e salva no banco vetorial.
    """
    # 1. Converter
    texto = extrair_texto_pdf(caminho_pdf)
    
    # 2. Chunking
    chunks = dividir_texto_em_chunks(texto)
    
    # 3. Indexar no ChromaDB
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadados = [{"origem": caminho_pdf} for _ in chunks]
    
    colecao.add(
        documents=chunks,
        metadatas=metadados,
        ids=ids
    )
    print(f"Documento {doc_id} indexado com sucesso! ({len(chunks)} chunks gerados)")

def indexar_toda_a_pasta_data():
    # Localiza a pasta 'data' a partir da posição deste script
    raiz_projeto = Path(__file__).resolve().parent.parent
    pasta_data = raiz_projeto / "data"
    
    # Procura por todos os arquivos que terminam com .pdf ou .PDF
    arquivos_pdf = list(pasta_data.glob("*.pdf")) + list(pasta_data.glob("*.PDF"))
    
    if not arquivos_pdf:
        print(f"Nenhum arquivo PDF encontrado em: {pasta_data}")
        return

    print(f"Encontrados {len(arquivos_pdf)} documentos para indexação.")
    
    # Loop para indexar cada um automaticamente
    for indice, caminho_pdf in enumerate(arquivos_pdf, start=1):
        # Cria um ID limpo usando o nome do arquivo (ex: "artigo_calculo")
        doc_id = f"doc_{caminho_pdf.stem.lower().replace(' ', '_')}"
        
        print(f"\n--- Processando [{indice}/{len(arquivos_pdf)}]: {caminho_pdf.name} ---")
        
        try:
            # Executa o pipeline: Docling -> Chunking -> ChromaDB
            indexar_documento(caminho_pdf=str(caminho_pdf), doc_id=doc_id)
        except Exception as e:
            print(f"Erro ao processar o arquivo {caminho_pdf.name}: {e}")

def buscar_material_rag(query: str) -> str:
    """
    Esta é a ferramenta (Tool) que o JARVIS (Gemma 12B) irá chamar.
    Ela busca a informação no banco e retorna o texto puro como contexto.
    """
    resultados = colecao.query(
        query_texts=[query],
        n_results=3 # Retorna os 3 chunks mais relevantes
    )
    
    textos_recuperados = resultados["documents"][0]
    
    # Junta os chunks encontrados em uma única string para devolver à LLM
    contexto_final = "\n\n---\n\n".join(textos_recuperados)
    return contexto_final

if __name__ == "__main__":
#     # Indexa o PDF apenas na primeira vez
      indexar_toda_a_pasta_data()
    
#     # Testa a ferramenta de busca
#     pergunta = "Como calcular o tempo de execução?"
#     resposta_rag = buscar_material_rag(pergunta)
    
#     print("=== CONTEXTO RECUPERADO ===")
#     print(resposta_rag)