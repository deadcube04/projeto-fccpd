"""
API Gateway - Desafio 3
Serviço web que integra banco de dados PostgreSQL e cache Redis.
Demonstra orquestração de múltiplos serviços com Docker Compose.
"""

import os
import json
import logging
import sys
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurações do PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'products_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres123')
}

# Configurações do Redis
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'redis'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'decode_responses': True
}

# Cache TTL (segundos)
CACHE_TTL = int(os.getenv('CACHE_TTL', 60))

# Clientes globais
redis_client = None
db_stats = {
    'queries': 0,
    'cache_hits': 0,
    'cache_misses': 0
}


def get_redis_client():
    """Obtém cliente Redis."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(**REDIS_CONFIG)
            redis_client.ping()
            logger.info("✓ Conectado ao Redis")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {e}")
            redis_client = None
    return redis_client


def get_db_connection():
    """Cria conexão com PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
        raise


def init_database():
    """Inicializa o banco de dados."""
    max_retries = 30
    retry_count = 0
    
    logger.info("Aguardando PostgreSQL ficar disponível...")
    
    while retry_count < max_retries:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Cria tabela de produtos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    stock INTEGER DEFAULT 0,
                    category VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Cria índice para busca por categoria
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_category 
                ON products(category)
            """)
            
            # Cria tabela de requisições (para demonstração)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS request_logs (
                    id SERIAL PRIMARY KEY,
                    endpoint VARCHAR(200),
                    method VARCHAR(10),
                    cache_hit BOOLEAN DEFAULT FALSE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("✓ Banco de dados inicializado com sucesso!")
            return True
            
        except Exception as e:
            retry_count += 1
            logger.warning(f"Tentativa {retry_count}/{max_retries}: PostgreSQL ainda não disponível")
            time.sleep(2)
    
    logger.error("✗ Falha ao conectar ao PostgreSQL")
    return False


def init_redis():
    """Inicializa Redis."""
    max_retries = 30
    retry_count = 0
    
    logger.info("Aguardando Redis ficar disponível...")
    
    while retry_count < max_retries:
        try:
            client = get_redis_client()
            if client:
                client.ping()
                logger.info("✓ Redis disponível!")
                return True
        except Exception:
            pass
        
        retry_count += 1
        logger.warning(f"Tentativa {retry_count}/{max_retries}: Redis ainda não disponível")
        time.sleep(2)
    
    logger.warning("⚠ Redis não disponível - continuando sem cache")
    return False


def log_request(endpoint, method, cache_hit=False):
    """Registra requisição no banco."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO request_logs (endpoint, method, cache_hit) VALUES (%s, %s, %s)",
            (endpoint, method, cache_hit)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Erro ao registrar requisição: {e}")


def get_from_cache(key):
    """Obtém valor do cache."""
    try:
        client = get_redis_client()
        if client:
            value = client.get(key)
            if value:
                db_stats['cache_hits'] += 1
                logger.info(f"✓ Cache HIT: {key}")
                return json.loads(value)
            else:
                db_stats['cache_misses'] += 1
                logger.info(f"✗ Cache MISS: {key}")
    except Exception as e:
        logger.error(f"Erro ao ler cache: {e}")
    return None


def set_to_cache(key, value, ttl=CACHE_TTL):
    """Salva valor no cache."""
    try:
        client = get_redis_client()
        if client:
            client.setex(key, ttl, json.dumps(value))
            logger.info(f"✓ Cache SET: {key} (TTL: {ttl}s)")
    except Exception as e:
        logger.error(f"Erro ao salvar no cache: {e}")


def invalidate_cache_pattern(pattern):
    """Invalida cache por padrão."""
    try:
        client = get_redis_client()
        if client:
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
                logger.info(f"✓ Cache invalidado: {pattern} ({len(keys)} chaves)")
    except Exception as e:
        logger.error(f"Erro ao invalidar cache: {e}")


@app.route('/')
def index():
    """Endpoint principal."""
    return jsonify({
        "service": "Product Catalog API",
        "version": "1.0.0",
        "services": {
            "database": "PostgreSQL",
            "cache": "Redis",
            "orchestration": "Docker Compose"
        },
        "endpoints": {
            "GET /": "API info",
            "GET /health": "Health check (all services)",
            "GET /products": "Lista produtos (com cache)",
            "POST /products": "Cria produto",
            "GET /products/<id>": "Obtém produto por ID (com cache)",
            "PUT /products/<id>": "Atualiza produto",
            "DELETE /products/<id>": "Remove produto",
            "GET /products/category/<category>": "Produtos por categoria",
            "GET /stats": "Estatísticas (DB + Cache)",
            "GET /cache/clear": "Limpa todo o cache",
            "GET /services": "Status dos serviços"
        }
    }), 200


@app.route('/health')
def health():
    """Health check de todos os serviços."""
    health_status = {
        "api": "healthy",
        "timestamp": datetime.now().isoformat()
    }
    
    # Verifica PostgreSQL
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"
    
    # Verifica Redis
    try:
        client = get_redis_client()
        if client:
            client.ping()
            health_status["cache"] = "healthy"
        else:
            health_status["cache"] = "disconnected"
    except Exception as e:
        health_status["cache"] = f"unhealthy: {str(e)}"
    
    # Status geral
    all_healthy = all(
        status == "healthy" 
        for key, status in health_status.items() 
        if key not in ["timestamp"]
    )
    
    status_code = 200 if all_healthy else 503
    
    return jsonify(health_status), status_code


@app.route('/services')
def services_status():
    """Status detalhado dos serviços."""
    status = {
        "database": {"connected": False, "config": DB_CONFIG.copy()},
        "cache": {"connected": False, "config": REDIS_CONFIG.copy()},
        "stats": db_stats.copy()
    }
    
    # Remove senhas das configs
    status["database"]["config"].pop("password", None)
    
    # Testa PostgreSQL
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM request_logs")
        request_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        status["database"]["connected"] = True
        status["database"]["products"] = product_count
        status["database"]["requests"] = request_count
    except Exception as e:
        status["database"]["error"] = str(e)
    
    # Testa Redis
    try:
        client = get_redis_client()
        if client:
            info = client.info()
            status["cache"]["connected"] = True
            status["cache"]["keys"] = client.dbsize()
            status["cache"]["memory_used"] = info.get("used_memory_human", "N/A")
            status["cache"]["uptime_seconds"] = info.get("uptime_in_seconds", 0)
    except Exception as e:
        status["cache"]["error"] = str(e)
    
    return jsonify(status), 200


@app.route('/products', methods=['GET'])
def get_products():
    """Lista todos os produtos (com cache)."""
    cache_key = "products:all"
    
    # Tenta obter do cache
    cached_data = get_from_cache(cache_key)
    if cached_data:
        log_request('/products', 'GET', cache_hit=True)
        return jsonify({
            "success": True,
            "source": "cache",
            "count": len(cached_data),
            "products": cached_data
        }), 200
    
    # Busca do banco
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        db_stats['queries'] += 1
        
        # Converte para dicionário
        products_list = [dict(p) for p in products]
        
        # Salva no cache
        set_to_cache(cache_key, products_list)
        
        log_request('/products', 'GET', cache_hit=False)
        
        logger.info(f"Listados {len(products_list)} produtos do banco")
        
        return jsonify({
            "success": True,
            "source": "database",
            "count": len(products_list),
            "products": products_list
        }), 200
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/products', methods=['POST'])
def create_product():
    """Cria um novo produto."""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'price']
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "error": "Campos obrigatórios: name, price"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            """
            INSERT INTO products (name, description, price, stock, category) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING *
            """,
            (
                data['name'],
                data.get('description', ''),
                data['price'],
                data.get('stock', 0),
                data.get('category', 'general')
            )
        )
        
        product = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        db_stats['queries'] += 1
        
        # Invalida cache
        invalidate_cache_pattern("products:*")
        
        logger.info(f"✓ Produto criado: {data['name']}")
        log_request('/products', 'POST', cache_hit=False)
        
        return jsonify({
            "success": True,
            "message": "Produto criado com sucesso",
            "product": dict(product)
        }), 201
    except Exception as e:
        logger.error(f"Erro ao criar produto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtém produto por ID (com cache)."""
    cache_key = f"product:{product_id}"
    
    # Tenta cache
    cached_data = get_from_cache(cache_key)
    if cached_data:
        log_request(f'/products/{product_id}', 'GET', cache_hit=True)
        return jsonify({
            "success": True,
            "source": "cache",
            "product": cached_data
        }), 200
    
    # Busca do banco
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        db_stats['queries'] += 1
        
        if not product:
            return jsonify({"success": False, "error": "Produto não encontrado"}), 404
        
        product_dict = dict(product)
        
        # Salva no cache
        set_to_cache(cache_key, product_dict)
        
        log_request(f'/products/{product_id}', 'GET', cache_hit=False)
        
        return jsonify({
            "success": True,
            "source": "database",
            "product": product_dict
        }), 200
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Atualiza produto."""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            """
            UPDATE products 
            SET name = COALESCE(%s, name),
                description = COALESCE(%s, description),
                price = COALESCE(%s, price),
                stock = COALESCE(%s, stock),
                category = COALESCE(%s, category),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
            """,
            (
                data.get('name'),
                data.get('description'),
                data.get('price'),
                data.get('stock'),
                data.get('category'),
                product_id
            )
        )
        
        product = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if not product:
            return jsonify({"success": False, "error": "Produto não encontrado"}), 404
        
        db_stats['queries'] += 1
        
        # Invalida cache
        invalidate_cache_pattern(f"product:{product_id}")
        invalidate_cache_pattern("products:*")
        
        logger.info(f"✓ Produto atualizado: ID {product_id}")
        log_request(f'/products/{product_id}', 'PUT', cache_hit=False)
        
        return jsonify({
            "success": True,
            "message": "Produto atualizado com sucesso",
            "product": dict(product)
        }), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar produto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Remove produto."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s RETURNING id", (product_id,))
        deleted = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if not deleted:
            return jsonify({"success": False, "error": "Produto não encontrado"}), 404
        
        db_stats['queries'] += 1
        
        # Invalida cache
        invalidate_cache_pattern(f"product:{product_id}")
        invalidate_cache_pattern("products:*")
        
        logger.info(f"✓ Produto removido: ID {product_id}")
        log_request(f'/products/{product_id}', 'DELETE', cache_hit=False)
        
        return jsonify({
            "success": True,
            "message": "Produto removido com sucesso"
        }), 200
    except Exception as e:
        logger.error(f"Erro ao remover produto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/products/category/<category>')
def get_products_by_category(category):
    """Obtém produtos por categoria (com cache)."""
    cache_key = f"products:category:{category}"
    
    # Tenta cache
    cached_data = get_from_cache(cache_key)
    if cached_data:
        log_request(f'/products/category/{category}', 'GET', cache_hit=True)
        return jsonify({
            "success": True,
            "source": "cache",
            "category": category,
            "count": len(cached_data),
            "products": cached_data
        }), 200
    
    # Busca do banco
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM products WHERE category = %s ORDER BY created_at DESC",
            (category,)
        )
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        db_stats['queries'] += 1
        
        products_list = [dict(p) for p in products]
        
        # Salva no cache
        set_to_cache(cache_key, products_list)
        
        log_request(f'/products/category/{category}', 'GET', cache_hit=False)
        
        return jsonify({
            "success": True,
            "source": "database",
            "category": category,
            "count": len(products_list),
            "products": products_list
        }), 200
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/stats')
def get_stats():
    """Estatísticas do sistema."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total de produtos
        cursor.execute("SELECT COUNT(*) as total FROM products")
        total_products = cursor.fetchone()['total']
        
        # Produtos por categoria
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM products 
            GROUP BY category
        """)
        by_category = cursor.fetchall()
        
        # Total de requisições
        cursor.execute("SELECT COUNT(*) as total FROM request_logs")
        total_requests = cursor.fetchone()['total']
        
        # Cache hits
        cursor.execute("""
            SELECT COUNT(*) as hits 
            FROM request_logs 
            WHERE cache_hit = TRUE
        """)
        cache_hits_db = cursor.fetchone()['hits']
        
        cursor.close()
        conn.close()
        
        # Estatísticas do Redis
        cache_stats = {}
        try:
            client = get_redis_client()
            if client:
                cache_stats = {
                    "keys": client.dbsize(),
                    "memory": client.info().get("used_memory_human", "N/A")
                }
        except:
            pass
        
        # Taxa de cache hit
        total_req = db_stats['cache_hits'] + db_stats['cache_misses']
        hit_rate = (db_stats['cache_hits'] / total_req * 100) if total_req > 0 else 0
        
        return jsonify({
            "success": True,
            "statistics": {
                "products": {
                    "total": total_products,
                    "by_category": {row['category']: row['count'] for row in by_category}
                },
                "requests": {
                    "total": total_requests,
                    "cache_hits": cache_hits_db,
                    "cache_hit_rate": f"{hit_rate:.2f}%"
                },
                "cache": cache_stats,
                "runtime_stats": db_stats
            }
        }), 200
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/cache/clear')
def clear_cache():
    """Limpa todo o cache."""
    try:
        client = get_redis_client()
        if client:
            client.flushdb()
            logger.info("✓ Cache limpo")
            return jsonify({
                "success": True,
                "message": "Cache limpo com sucesso"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Redis não disponível"
            }), 503
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("Iniciando Product Catalog API")
    logger.info(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    logger.info(f"Cache: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
    logger.info(f"Cache TTL: {CACHE_TTL}s")
    logger.info("=" * 70)
    
    # Inicializa serviços
    db_ready = init_database()
    redis_ready = init_redis()
    
    if db_ready:
        logger.info("✓ Todos os serviços inicializados!")
        logger.info("Servidor pronto na porta 8000")
        app.run(host='0.0.0.0', port=8000, debug=False)
    else:
        logger.error("✗ Falha ao inicializar serviços")
        sys.exit(1)
