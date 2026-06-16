import os
import json
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Importe suas funções reais
from database import consultar_agenda, listar_tarefas, adicionar_tarefa, concluir_tarefa, adicionar_evento_agenda
from rag import buscar_material_rag 

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL")
)
MODELO = 'Qwen/Qwen2.5-14B-Instruct-AWQ'

# ==========================================
# SEÇÃO 5: MELHORIAS DE APRENDIZADO
# ==========================================

def gerar_exercicios(topico: str, quantidade: int = 3) -> str:
    """Ferramenta 1 (Aprendizado): Cria uma lista de exercícios baseados no RAG."""
    contexto = buscar_material_rag(topico)
    
    # Devolvemos o contexto com uma instrução forte para a IA criar o questionário
    return f"CONTEXTO RECUPERADO:\n{contexto}\n\nINSTRUÇÃO INTERNA OBRIGATÓRIA: Usando estritamente o contexto acima, crie {quantidade} exercícios práticos sobre '{topico}'. No final da sua resposta, forneça o gabarito comentado."

def iniciar_active_recall(topico: str) -> str:
    """
    Ferramenta 2 (Interativa): Pausa o assistente, faz uma pergunta ao usuário,
    lê a resposta no terminal e faz a avaliação crítica.
    """
    print(f"\n[🧠 Iniciando Active Recall sobre: '{topico}']")
    
    # 1. Busca a teoria no banco vetorial
    contexto = buscar_material_rag(topico)
    
    # 2. Pede para a LLM criar a pergunta isolada
    print("[⏳ JARVIS está formulando a pergunta...]")
    resp_pergunta = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": "Você é um professor universitário rigoroso. Com base no texto a seguir, crie UMA única pergunta direta, conceitual e desafiadora para testar o aluno. NÃO escreva a resposta."},
            {"role": "user", "content": f"Texto de base:\n{contexto}"}
        ]
    )
    pergunta = resp_pergunta.choices[0].message.content
    
    # 3. Interação no Terminal (O sistema pausa e aguarda o aluno)
    print("\n" + "="*50)
    resposta_aluno = input(f"❓ PERGUNTA DO JARVIS:\n{pergunta}\n\nSua Resposta: ")
    print("="*50)
    
    # 4. Pede para a LLM avaliar a resposta do aluno cruzando com o PDF
    print("\n[⏳ JARVIS está avaliando sua resposta...]")
    resp_avaliacao = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": "Você é um professor avaliando a resposta do aluno. Classifique em: CORRETA, PARCIALMENTE CORRETA ou INCORRETA. Depois, justifique apontando o que faltou e ensinando a teoria correta baseada no texto."},
            {"role": "user", "content": f"Texto de referência:\n{contexto}\n\nPergunta feita: {pergunta}\nResposta do Aluno: {resposta_aluno}"}
        ]
    )
    avaliacao = resp_avaliacao.choices[0].message.content
    
    # Imprime a nota na tela imediatamente
    print(f"\n📝 AVALIAÇÃO:\n{avaliacao}\n")
    
    # Devolve o contexto final para o loop principal do JARVIS
    return f"O usuário completou um Active Recall sobre '{topico}'. O desempenho dele já foi avaliado em tela. Faça um breve comentário de encorajamento para continuarmos os estudos."

FUNCOES_DISPONIVEIS = {
    "consultar_agenda": consultar_agenda,
    "adicionar_evento_agenda": adicionar_evento_agenda,
    "listar_tarefas": listar_tarefas,
    "adicionar_tarefa": adicionar_tarefa,
    "concluir_tarefa": concluir_tarefa,
    "buscar_material_rag": buscar_material_rag,
    "gerar_exercicios": gerar_exercicios,
    "iniciar_active_recall": iniciar_active_recall
}

def registrar_log(ferramenta: str, entrada: dict, saida: str):
    """Gera um log de cada chamada de ferramenta (Requisito 4)."""
    os.makedirs("logs", exist_ok=True)
    with open("logs/logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
        f.write(f"Ferramenta Chamada: {ferramenta}\n")
        f.write(f"Entrada (Parâmetros): {json.dumps(entrada, ensure_ascii=False)}\n")
        f.write(f"Saída (Resultado): {saida}\n")
        f.write("-" * 50 + "\n")

def tentar_extrair_json(texto: str):
    """Tenta encontrar e interpretar um bloco JSON dentro da resposta de texto da IA."""
    try:
        # Procura por tudo que está entre chaves {}
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except json.JSONDecodeError:
        return None

def iniciar_jarvis():
    print("🤖 JARVIS Acadêmico Inicializado. (Digite 'sair' para encerrar)")
    
    #Captura a data exata do sistema toda vez que roda
    hoje = datetime.now()
    data_atual = hoje.strftime("%Y-%m-%d")
    dias_da_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    dia_semana = dias_da_semana[hoje.weekday()]

    # 1. O Novo Prompt de Sistema (Ensina a IA a usar as ferramentas manualmente)
    instrucoes_ferramentas = f"""
    Você é o JARVIS, um assistente acadêmico inteligente para estudantes de software.

    CONHECIMENTO TEMPORAL IMPORTANTE:
    - Hoje é {dia_semana}, data: {data_atual}.
    - Use esta data como base matemática (D0) SEMPRE que o usuário usar termos relativos como "hoje", "amanhã", "depois de amanhã", "próxima semana" ou "este mês" para preencher os parâmetros das ferramentas.

    Você tem ferramentas para buscar dados. SE PRECISA BUSCAR DADOS, você deve responder ÚNICA e EXCLUSIVAMENTE com um bloco JSON estruturado exatamente assim:
    {{"ferramenta": "nome_da_ferramenta", "parametros": {{"chave": "valor"}}}}

    Ferramentas disponíveis:
    1. "consultar_agenda": parâmetros: "data_inicio" (YYYY-MM-DD), "data_fim" (YYYY-MM-DD).
    2. "adicionar_evento_agenda": parâmetros: "evento" (texto), "data_hora" (YYYY-MM-DD HH:MM), "descricao" (texto).
    3. "listar_tarefas": parâmetros: "status" ("todas", "pendente", "concluída").
    4. "adicionar_tarefa": parâmetros: "descricao" (texto).
    5. "concluir_tarefa": parâmetros: "id_tarefa" (número inteiro).
    6. "buscar_material_rag": parâmetros: "query" (texto da busca).
    7. "gerar_exercicios": parâmetros: "topico" (texto), "quantidade" (inteiro). Use quando o usuário quiser lista de exercícios para praticar depois.
    8. "iniciar_active_recall": parâmetros: "topico" (texto). Use quando o usuário quiser testar os conhecimentos AGORA, de forma interativa.

    Se você JÁ TEM a resposta, responda normalmente ao usuário em português. Não misture texto natural com o bloco JSON na mesma resposta.
    """

    mensagens = [{"role": "system", "content": instrucoes_ferramentas}]

    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() in ['sair', 'exit']:
            print("Encerrando o JARVIS. Bons estudos!")
            break

        mensagens.append({"role": "user", "content": user_input})

        try:
            # CHAMADA 1: Pergunta à IA (sem enviar o array 'tools' que quebra o servidor)
            resposta = client.chat.completions.create(
                model=MODELO,
                messages=mensagens
            )
            
            texto_ia = resposta.choices[0].message.content
            
            # 2. Analisa se a IA respondeu com um JSON (Tentativa de Tool Calling)
            dados_ferramenta = tentar_extrair_json(texto_ia)
            
            if dados_ferramenta and "ferramenta" in dados_ferramenta:
                nome_funcao = dados_ferramenta["ferramenta"]
                argumentos = dados_ferramenta.get("parametros", {})
                
                print(f"\n[⚙️ JARVIS acionando: {nome_funcao} com parâmetros {argumentos} ...]")
                
                # Executa a função Python
                funcao_python = FUNCOES_DISPONIVEIS.get(nome_funcao)
                if funcao_python:
                    try:
                        resultado = funcao_python(**argumentos)
                    except Exception as e:
                        resultado = f"Erro ao executar os parâmetros: {e}"
                else:
                    resultado = f"Erro: Ferramenta {nome_funcao} não existe."
                
                # Salva o log obrigatório
                registrar_log(nome_funcao, argumentos, str(resultado))
                
                # 3. Adiciona o resultado na conversa e pede para a IA formular a resposta final
                # Salvamos o bloco JSON que ela gerou para manter o contexto
                mensagens.append({"role": "assistant", "content": texto_ia}) 
                
                # Informamos o resultado como se fosse o sistema falando
                mensagem_resultado = f"RESULTADO DA FERRAMENTA '{nome_funcao}':\n{resultado}\n\nAgora responda ao usuário em linguagem natural usando este resultado."
                mensagens.append({"role": "user", "content": mensagem_resultado})
                
                # CHAMADA 2: IA lê o resultado e escreve a resposta final
                resposta_final = client.chat.completions.create(
                    model=MODELO,
                    messages=mensagens
                )
                
                texto_final = resposta_final.choices[0].message.content
                mensagens.append({"role": "assistant", "content": texto_final})
                print(f"\nJARVIS: {texto_final}")
                
            else:
                # Se não tem JSON, é apenas a IA conversando normalmente
                mensagens.append({"role": "assistant", "content": texto_ia})
                print(f"\nJARVIS: {texto_ia}")
                
        except Exception as e:
            erro_str = str(e)
            if "502 Bad Gateway" in erro_str:
                print("\n[🚨 ERRO 502]: O servidor da IA está fora do ar ou reiniciando. Tente novamente em alguns minutos.")
            elif "400" in erro_str:
                print(f"\n[⚠️ ERRO 400]: Requisição mal formatada ou bloqueada pelo servidor. Detalhes: {erro_str}")
            else:
                print(f"\n[Erro de Comunicação com a API]: {erro_str}")

if __name__ == "__main__":
    iniciar_jarvis()