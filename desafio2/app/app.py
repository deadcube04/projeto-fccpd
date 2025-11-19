"""
Aplicação de Gerenciamento de Tarefas - Desafio 2
Aplicação Flask que gerencia tarefas em um banco PostgreSQL com persistência.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request
from datetime import datetime
import logging
import sys
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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


def init_database():
    """Inicializa o banco de dados e cria as tabelas necessárias."""
    max_retries = 30
    retry_count = 0
    
    logger.info("Aguardando PostgreSQL ficar disponível...")
    
    while retry_count < max_retries:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Cria tabela de tarefas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Cria tabela de logs de operações
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id SERIAL PRIMARY KEY,
                    operation VARCHAR(50) NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("✓ Banco de dados inicializado com sucesso!")
            
            # Registra inicialização
            log_operation("INIT", "Banco de dados inicializado")
            
            return True
            
        except Exception as e:
            retry_count += 1
            logger.warning(f"Tentativa {retry_count}/{max_retries}: PostgreSQL ainda não disponível")
            time.sleep(2)
    
    logger.error("✗ Falha ao conectar ao PostgreSQL após múltiplas tentativas")
    return False


def log_operation(operation, description):
    """Registra uma operação no banco de dados."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO operation_logs (operation, description) VALUES (%s, %s)",
            (operation, description)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Erro ao registrar operação: {e}")


@app.route('/')
def index():
    """Endpoint principal com informações da API."""
    return jsonify({
        "service": "Task Manager API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API info",
            "GET /health": "Health check",
            "GET /tasks": "Lista todas as tarefas",
            "POST /tasks": "Cria nova tarefa",
            "GET /tasks/<id>": "Obtém tarefa por ID",
            "PUT /tasks/<id>": "Atualiza tarefa",
            "DELETE /tasks/<id>": "Remove tarefa",
            "GET /stats": "Estatísticas do banco",
            "GET /logs": "Logs de operações"
        }
    }), 200


@app.route('/health')
def health():
    """Health check com verificação de conexão ao banco."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Lista todas as tarefas."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
        
        logger.info(f"Listadas {len(tasks)} tarefas")
        
        return jsonify({
            "success": True,
            "count": len(tasks),
            "tasks": [dict(task) for task in tasks]
        }), 200
    except Exception as e:
        logger.error(f"Erro ao listar tarefas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/tasks', methods=['POST'])
def create_task():
    """Cria uma nova tarefa."""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({"success": False, "error": "Campo 'title' é obrigatório"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            """
            INSERT INTO tasks (title, description, status) 
            VALUES (%s, %s, %s) 
            RETURNING *
            """,
            (data['title'], data.get('description', ''), data.get('status', 'pending'))
        )
        
        task = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✓ Tarefa criada: {data['title']}")
        log_operation("CREATE", f"Tarefa criada: {data['title']}")
        
        return jsonify({
            "success": True,
            "message": "Tarefa criada com sucesso",
            "task": dict(task)
        }), 201
    except Exception as e:
        logger.error(f"Erro ao criar tarefa: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Obtém uma tarefa específica por ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not task:
            return jsonify({"success": False, "error": "Tarefa não encontrada"}), 404
        
        return jsonify({
            "success": True,
            "task": dict(task)
        }), 200
    except Exception as e:
        logger.error(f"Erro ao buscar tarefa: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Atualiza uma tarefa existente."""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            """
            UPDATE tasks 
            SET title = COALESCE(%s, title),
                description = COALESCE(%s, description),
                status = COALESCE(%s, status),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
            """,
            (data.get('title'), data.get('description'), data.get('status'), task_id)
        )
        
        task = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if not task:
            return jsonify({"success": False, "error": "Tarefa não encontrada"}), 404
        
        logger.info(f"✓ Tarefa atualizada: ID {task_id}")
        log_operation("UPDATE", f"Tarefa atualizada: ID {task_id}")
        
        return jsonify({
            "success": True,
            "message": "Tarefa atualizada com sucesso",
            "task": dict(task)
        }), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar tarefa: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Remove uma tarefa."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
        deleted = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if not deleted:
            return jsonify({"success": False, "error": "Tarefa não encontrada"}), 404
        
        logger.info(f"✓ Tarefa removida: ID {task_id}")
        log_operation("DELETE", f"Tarefa removida: ID {task_id}")
        
        return jsonify({
            "success": True,
            "message": "Tarefa removida com sucesso"
        }), 200
    except Exception as e:
        logger.error(f"Erro ao remover tarefa: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/stats')
def get_stats():
    """Retorna estatísticas do banco de dados."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total de tarefas
        cursor.execute("SELECT COUNT(*) as total FROM tasks")
        total = cursor.fetchone()['total']
        
        # Tarefas por status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM tasks 
            GROUP BY status
        """)
        by_status = cursor.fetchall()
        
        # Total de operações
        cursor.execute("SELECT COUNT(*) as total FROM operation_logs")
        operations = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "statistics": {
                "total_tasks": total,
                "by_status": {row['status']: row['count'] for row in by_status},
                "total_operations": operations
            }
        }), 200
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/logs')
def get_logs():
    """Retorna os logs de operações."""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM operation_logs ORDER BY timestamp DESC LIMIT %s",
            (limit,)
        )
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "count": len(logs),
            "logs": [dict(log) for log in logs]
        }), 200
    except Exception as e:
        logger.error(f"Erro ao obter logs: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Iniciando Task Manager API")
    logger.info(f"Banco: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    logger.info("=" * 60)
    
    if init_database():
        logger.info("Servidor pronto para receber requisições na porta 5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        logger.error("Falha ao inicializar banco de dados. Encerrando...")
        sys.exit(1)
