import sqlite3
from datetime import datetime, timedelta
from database import DB_PATH, adicionar_tarefa, obter_conexao

def popular_dados_teste():
    print("Iniciando inserção de dados de teste...")
    
    # 1. Inserindo Tarefas (usando a própria ferramenta que criamos)
    adicionar_tarefa("Revisar políticas de write-back e mapeamento direto de cache")
    adicionar_tarefa("Refatorar gerenciamento de estado do React para o painel de funcionários")
    adicionar_tarefa("Configurar Dockerfile do backend em Spring Boot")
    
    # Marcando a primeira como concluída para testar o filtro
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.execute("UPDATE Tarefas SET status = 'concluída' WHERE id = 1")
        conexao.commit()
    print("Tarefas inseridas com sucesso.")

    # 2. Inserindo Eventos na Agenda
    hoje = datetime.now()
    amanha = hoje + timedelta(days=1)
    proxima_semana = hoje + timedelta(days=7)
    
    eventos = [
        ("Prova de Arquitetura de Computadores", "Foco em cálculo de CPI e hierarquia de memória", hoje.strftime("%Y-%m-%d 19:00")),
        ("Entrega do Projeto JARVIS", "Subir o repositório e gravar o vídeo de 3 minutos", amanha.strftime("%Y-%m-%d 23:59")),
        ("Reunião do Grupo", "Discutir a integração do modelo Gemma 12B com o SQLite", proxima_semana.strftime("%Y-%m-%d 14:00"))]
    
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.executemany(
            "INSERT INTO Agenda (evento, descricao, data_hora) VALUES (?, ?, ?)", 
            eventos
        )
        conexao.commit()
    print("Eventos da agenda inseridos com sucesso.")

if __name__ == "__main__":
    popular_dados_teste()