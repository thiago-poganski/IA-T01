import sqlite3
from datetime import datetime
from pathlib import Path

# 1. Encontra a raiz do projeto (voltando uma pasta a partir de 'src')
RAIZ_PROJETO = Path(__file__).resolve().parent.parent

# 2. Define e cria a pasta 'db' na raiz (se ela ainda não existir)
PASTA_DB = RAIZ_PROJETO / "db"
PASTA_DB.mkdir(exist_ok=True)

# 3. Define o caminho final do arquivo SQLite
DB_PATH = PASTA_DB / "jarvis_academico.db"

def obter_conexao():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    return sqlite3.connect(DB_PATH)

def inicializar_banco():
    """Cria as tabelas de Agenda e Tarefas se não existirem."""
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        
        # Tabela de Tarefas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                status TEXT DEFAULT 'pendente',
                data_criacao TEXT NOT NULL
            )
        """)
        
        # Tabela de Agenda
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Agenda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evento TEXT NOT NULL,
                descricao TEXT,
                data_hora TEXT NOT NULL
            )
        """)
        conexao.commit()
    print("Banco de dados inicializado com sucesso!")

# ==========================================
# FERRAMENTAS DA LISTA DE TAREFAS (SEÇÃO 3.3)
# ==========================================

def adicionar_tarefa(descricao: str) -> str:
    """Ferramenta para adicionar uma nova tarefa."""
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO Tarefas (descricao, data_criacao) VALUES (?, ?)", 
            (descricao, data_atual)
        )
        conexao.commit()
        id_tarefa = cursor.lastrowid
        
    return f"Sucesso: Tarefa '{descricao}' adicionada com o ID {id_tarefa}."

def listar_tarefas(status: str = "todas") -> str:
    """Ferramenta para listar tarefas. Status pode ser 'pendente', 'concluída' ou 'todas'."""
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        if status.lower() == "todas":
            cursor.execute("SELECT id, descricao, status FROM Tarefas")
        else:
            cursor.execute("SELECT id, descricao, status FROM Tarefas WHERE status = ?", (status.lower(),))
        
        tarefas = cursor.fetchall()
        
    if not tarefas:
        return f"Nenhuma tarefa encontrada com o status: {status}."
    
    # Formata a saída em texto para a LLM entender melhor
    resultado = f"--- TAREFAS ({status.upper()}) ---\n"
    for t in tarefas:
        resultado += f"[ID: {t[0]}] {t[1]} - Status: {t[2]}\n"
    return resultado

def concluir_tarefa(id_tarefa: int) -> str:
    """Ferramenta para marcar uma tarefa como concluída pelo seu ID."""
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        # Verifica se a tarefa existe
        cursor.execute("SELECT id FROM Tarefas WHERE id = ?", (id_tarefa,))
        if not cursor.fetchone():
            return f"Erro: Tarefa com ID {id_tarefa} não encontrada."
            
        cursor.execute("UPDATE Tarefas SET status = 'concluída' WHERE id = ?", (id_tarefa,))
        conexao.commit()
        
    return f"Sucesso: Tarefa ID {id_tarefa} marcada como concluída."

# ==========================================
# FERRAMENTAS DA AGENDA ACADÊMICA (SEÇÃO 3.2)
# ==========================================

def consultar_agenda(data_inicio: str, data_fim: str) -> str:
    """
    Ferramenta para buscar eventos na agenda. 
    O formato esperado das datas é 'YYYY-MM-DD'.
    """
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        # Busca eventos que ocorrem no intervalo de datas fornecido
        cursor.execute("""
            SELECT id, evento, descricao, data_hora 
            FROM Agenda 
            WHERE date(data_hora) BETWEEN date(?) AND date(?)
            ORDER BY data_hora ASC
        """, (data_inicio, data_fim))
        
        eventos = cursor.fetchall()

    if not eventos:
        return f"Nenhum evento agendado entre {data_inicio} e {data_fim}."
    
    resultado = f"--- EVENTOS DE {data_inicio} A {data_fim} ---\n"
    for e in eventos:
        resultado += f"[{e[3]}] {e[1]} (ID: {e[0]}) - Descrição: {e[2]}\n"
    return resultado

def adicionar_evento_agenda(evento: str, data_hora: str, descricao: str = "") -> str:
    """
    Ferramenta para adicionar um novo compromisso, aula ou prova na agenda.
    O formato de data_hora esperado é 'YYYY-MM-DD HH:MM'.
    """
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO Agenda (evento, descricao, data_hora) VALUES (?, ?, ?)", 
            (evento, descricao, data_hora)
        )
        conexao.commit()
        id_evento = cursor.lastrowid
        
    return f"Sucesso: Evento '{evento}' adicionado para {data_hora} com ID {id_evento}."

# Executa a inicialização ao rodar o script
# if __name__ == "__main__":
#     inicializar_banco()