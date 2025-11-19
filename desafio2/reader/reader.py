"""
Leitor de Dados - Desafio 2
Container separado que lê e exibe dados persistidos no volume PostgreSQL.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys
import time
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'tasks_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres123')
}


def get_db_connection():
    """Cria conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        raise


def wait_for_database():
    """Aguarda o banco de dados ficar disponível."""
    max_retries = 30
    retry_count = 0
    
    logger.info("Aguardando PostgreSQL ficar disponível...")
    
    while retry_count < max_retries:
        try:
            conn = get_db_connection()
            conn.close()
            logger.info("✓ PostgreSQL disponível!")
            return True
        except Exception:
            retry_count += 1
            logger.info(f"Tentativa {retry_count}/{max_retries}: Aguardando PostgreSQL...")
            time.sleep(2)
    
    logger.error("✗ PostgreSQL não ficou disponível")
    return False


def read_tasks():
    """Lê todas as tarefas do banco de dados."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT COUNT(*) as count FROM tasks")
        count = cursor.fetchone()['count']
        
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return count, [dict(task) for task in tasks]
    except Exception as e:
        logger.error(f"Erro ao ler tarefas: {e}")
        return 0, []


def read_logs():
    """Lê os logs de operações."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT COUNT(*) as count FROM operation_logs")
        count = cursor.fetchone()['count']
        
        cursor.execute("SELECT * FROM operation_logs ORDER BY timestamp DESC LIMIT 20")
        logs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return count, [dict(log) for log in logs]
    except Exception as e:
        logger.error(f"Erro ao ler logs: {e}")
        return 0, []


def get_statistics():
    """Obtém estatísticas do banco de dados."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total de tarefas
        cursor.execute("SELECT COUNT(*) as total FROM tasks")
        total_tasks = cursor.fetchone()['total']
        
        # Tarefas por status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM tasks 
            GROUP BY status
        """)
        by_status = cursor.fetchall()
        
        # Total de operações
        cursor.execute("SELECT COUNT(*) as total FROM operation_logs")
        total_operations = cursor.fetchone()['total']
        
        # Primeira e última tarefa
        cursor.execute("""
            SELECT MIN(created_at) as first, MAX(created_at) as last 
            FROM tasks
        """)
        dates = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            'total_tasks': total_tasks,
            'by_status': {row['status']: row['count'] for row in by_status},
            'total_operations': total_operations,
            'first_task': dates['first'],
            'last_task': dates['last']
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return None


def print_separator(char="=", length=70):
    """Imprime uma linha separadora."""
    print(char * length)


def display_data():
    """Exibe os dados persistidos no banco."""
    print_separator()
    print("📊 LEITOR DE DADOS PERSISTIDOS - DESAFIO 2")
    print_separator()
    print()
    
    # Estatísticas gerais
    logger.info("Coletando estatísticas do banco de dados...")
    stats = get_statistics()
    
    if stats:
        print("📈 ESTATÍSTICAS GERAIS")
        print_separator("-")
        print(f"  Total de tarefas: {stats['total_tasks']}")
        
        if stats['by_status']:
            print(f"  Tarefas por status:")
            for status, count in stats['by_status'].items():
                print(f"    • {status}: {count}")
        
        print(f"  Total de operações registradas: {stats['total_operations']}")
        
        if stats['first_task']:
            print(f"  Primeira tarefa: {stats['first_task']}")
        if stats['last_task']:
            print(f"  Última tarefa: {stats['last_task']}")
        print()
    
    # Lista de tarefas
    logger.info("Lendo tarefas...")
    count, tasks = read_tasks()
    
    print("📝 TAREFAS CADASTRADAS")
    print_separator("-")
    
    if count == 0:
        print("  Nenhuma tarefa encontrada.")
    else:
        print(f"  Total: {count} tarefa(s)\n")
        
        for i, task in enumerate(tasks, 1):
            print(f"  [{i}] ID: {task['id']}")
            print(f"      Título: {task['title']}")
            if task['description']:
                print(f"      Descrição: {task['description']}")
            print(f"      Status: {task['status']}")
            print(f"      Criada em: {task['created_at']}")
            if task['updated_at'] != task['created_at']:
                print(f"      Atualizada em: {task['updated_at']}")
            print()
    
    # Logs de operações
    logger.info("Lendo logs de operações...")
    log_count, logs = read_logs()
    
    print("📋 LOGS DE OPERAÇÕES (últimos 20)")
    print_separator("-")
    
    if log_count == 0:
        print("  Nenhum log encontrado.")
    else:
        print(f"  Total de operações: {log_count}\n")
        
        for i, log in enumerate(logs, 1):
            print(f"  [{i}] {log['operation']} - {log['description']}")
            print(f"      {log['timestamp']}")
            print()
    
    print_separator()
    print("✅ Demonstração de persistência de dados concluída!")
    print("   Os dados acima foram lidos diretamente do volume Docker persistido.")
    print_separator()


if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("LEITOR DE DADOS PERSISTIDOS")
    logger.info(f"Banco: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    logger.info("=" * 70)
    print()
    
    if wait_for_database():
        try:
            display_data()
        except KeyboardInterrupt:
            logger.info("\nLeitura interrompida pelo usuário")
        except Exception as e:
            logger.error(f"Erro durante leitura: {e}")
            sys.exit(1)
    else:
        logger.error("Não foi possível conectar ao banco de dados")
        sys.exit(1)
