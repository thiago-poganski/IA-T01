from pypdf import PdfReader
from pathlib import Path

def extrair_texto_pdf(caminho_pdf: str) -> str:
    """
    Extrai o texto do PDF de forma rápida e com baixo consumo de memória.
    """
    nome_arquivo = Path(caminho_pdf).name
    print(f"Extraindo texto de: {nome_arquivo}...")
    
    texto_completo = []
    
    try:
        leitor = PdfReader(caminho_pdf)
        for num_pagina, pagina in enumerate(leitor.pages):
            texto_pagina = pagina.extract_text()
            
            if texto_pagina:
                # Adiciona uma marcação simples de página para ajudar o RAG
                texto_completo.append(f"--- PÁGINA {num_pagina + 1} ---\n{texto_pagina}")
                
        print(f"Extração concluída: {len(leitor.pages)} páginas lidas.")
    except Exception as e:
         print(f"Erro ao ler o PDF {nome_arquivo}: {e}")
         
    # Junta as páginas com quebras duplas de linha
    return "\n\n".join(texto_completo)