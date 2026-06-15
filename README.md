# TRABALHO PRÁTICO – JARVIS ACADÊMICO (ASSISTENTE INTELIGENTE PARA ESTUDANTES)

(Obs: descomente as linhas finais 'if __name__ == "__main__":' para rodar os arquivos fora o agente.py)
1. Rode rag.py  para gerar os chunks
2. Rode database.py para criar o  banco de dados das tarefas e da agenda
3. Rode popular_banco.py para  preencher o banco de dados com dados iniciais
4. Rode agente.py para usar o agente

# Documentação do Dataset

* **Origem dos Dados:** Livros e artigos em PDF.
* **Tipo de Conteúdo:** Conteúdo acadêmico puramente textual extraído através da biblioteca PyPDF.
* **Limitações:** A extração não preserva tabelas complexas, imagens e formatações estruturais pesadas, o que pode causar perda de contexto em fórmulas matemáticas ou gráficos geométricos.
* **Estratégia de Chunking:** Utilizamos o `RecursiveCharacterTextSplitter` da biblioteca LangChain, com `chunk_size=1000` e `chunk_overlap=150`, separados preferencialmente por parágrafos (`\n\n`) e linhas.
* **Impacto no RAG:** A sobreposição (overlap) de 150 caracteres garante que contextos divididos entre duas páginas não percam o sentido semântico, melhorando a assertividade do motor vetorial (all-MiniLM-L6-v2) na hora de recuperar a teoria para a IA.