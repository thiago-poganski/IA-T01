# Erro 1: Estouro de Memória na Ingestão de Dados (std::bad_alloc)  
## Tipo de Falha: Ingestão de Dados / Processamento.

## Causa: Durante a conversão dos PDFs acadêmicos para Markdown, páginas específicas contendo gráficos vetoriais hipercomplexos ou imagens de altíssima resolução sobrecarregaram o motor C++ do Docling, esgotando a memória RAM disponível e derrubando o processo.

## Possível Solução (Aplicada): Substituição da biblioteca de extração por uma solução mais leve e resiliente (pypdf), abrindo mão da formatação Markdown perfeita em prol da estabilidade do pipeline, garantindo a extração do texto puro sem estourar o limite de memória.

# Erro 2: Recusa de Chamada de Ferramenta Nativa (HTTP 400 BadRequest)
## Tipo de Falha: Integração de API / Tool Calling.

## Causa: Ao enviar o JSON Schema nativo da OpenAI, o servidor rodando o modelo Gemma 12B (via vLLM) recusou a requisição porque o motor não foi inicializado com as flags --enable-auto-tool-choice e --tool-call-parser, impossibilitando o uso do parâmetro tools.

## Possível Solução (Aplicada): Implementação de uma arquitetura ReAct (Reasoning and Acting) / Tool Calling Manual. O mapeamento de ferramentas foi transferido para o System Prompt, ensinando o modelo a responder com um bloco JSON estruturado em texto plano, que é interceptado via Regex no Python para a execução local das ferramentas.

# Erro 3: Alucinação Temporal
## Tipo de Falha: Geração / Contexto.

## Causa: Inicialmente, o sistema não conseguia processar comandos com termos de tempo relativo (como "hoje", "amanhã", "próxima semana"). Como a LLM não tem consciência do tempo real, ela alucinava datas aleatórias ao tentar preencher os parâmetros da ferramenta consultar_agenda.

## Possível Solução (Aplicada): Injeção dinâmica de contexto temporal. O script Python foi ajustado para capturar a data do sistema via datetime.now() e injetar o dia da semana e a data exata como a "base matemática (D0)" no System Prompt antes de cada requisição.