from langchain_text_splitters import RecursiveCharacterTextSplitter

def dividir_texto_em_chunks(texto_markdown: str) -> list[str]:
    """
    Divide o markdown em chunks menores, priorizando quebras de parágrafo e estrutura.
    """
    separadores = [
        "\n\n",   # Parágrafos
        "\n",     # Linhas
        " ",      # Palavras
        ""        # Caracteres (fallback de segurança)
    ]
    
    splitter = RecursiveCharacterTextSplitter(
        separators=separadores,
        chunk_size=1000,
        chunk_overlap=150, # Sobreposição para não perder o contexto entre chunks
        length_function=len
    )
    
    chunks = splitter.split_text(texto_markdown)
    return chunks