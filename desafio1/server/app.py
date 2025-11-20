from flask import Flask, jsonify, request
from datetime import datetime
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

request_counter = 0


@app.route('/', methods=['GET'])
def index():
    global request_counter
    request_counter += 1
    
    client_ip = request.remote_addr
    timestamp = datetime.now().isoformat()
    
    logger.info(f"Requisição #{request_counter} recebida de {client_ip}")
    
    response_data = {
        "status": "success",
        "message": "Servidor Flask em execução!",
        "timestamp": timestamp,
        "request_number": request_counter,
        "client_ip": client_ip,
        "server": "desafio1-server"
    }
    
    return jsonify(response_data), 200


@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check requisitado")
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_requests": request_counter
    }), 200


@app.route('/stats', methods=['GET'])
def stats():
    logger.info("Estatísticas requisitadas")
    return jsonify({
        "total_requests": request_counter,
        "timestamp": datetime.now().isoformat(),
        "uptime_message": "Servidor operacional"
    }), 200


@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Rota não encontrada: {request.path}")
    return jsonify({
        "status": "error",
        "message": "Endpoint não encontrado",
        "path": request.path
    }), 404


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Iniciando servidor Flask na porta 8080")
    logger.info("Endpoints disponíveis:")
    logger.info("  - GET /         : Endpoint principal")
    logger.info("  - GET /health   : Health check")
    logger.info("  - GET /stats    : Estatísticas do servidor")
    logger.info("=" * 60)
    
    app.run(host='0.0.0.0', port=8080, debug=False)
