from flask import Flask, jsonify, request
from datetime import datetime
import requests
import logging
from typing import Dict, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

USERS_SERVICE_URL = "http://users-service:5001"
ORDERS_SERVICE_URL = "http://orders-service:5002"

REQUEST_TIMEOUT = 5

STATS = {
    'total_requests': 0,
    'users_requests': 0,
    'orders_requests': 0,
    'errors': 0,
    'start_time': datetime.now().isoformat()
}


class ServiceClient:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'APIGateway/1.0',
            'Accept': 'application/json'
        })
    
    def make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Tuple[Optional[Dict], int]:

        try:
            kwargs.setdefault('timeout', REQUEST_TIMEOUT)
            
            response = self.session.request(method, url, **kwargs)
            
            try:
                data = response.json()
            except ValueError:
                data = {'response': response.text}
            
            return data, response.status_code
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling {url}")
            return {'error': 'Service timeout'}, 504
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {url}")
            return {'error': 'Service unavailable'}, 503
            
        except Exception as e:
            logger.error(f"Error calling {url}: {e}")
            return {'error': 'Internal gateway error'}, 500


service_client = ServiceClient()


@app.before_request
def before_request():
    STATS['total_requests'] += 1
    logger.info(f"{request.method} {request.path} - Client: {request.remote_addr}")


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'API Gateway',
        'version': '1.0.0',
        'description': 'Ponto único de entrada para acesso aos microsserviços',
        'services': {
            'users': USERS_SERVICE_URL,
            'orders': ORDERS_SERVICE_URL
        },
        'endpoints': {
            'users': {
                'list': 'GET /users',
                'get': 'GET /users/<id>',
                'create': 'POST /users',
                'update': 'PUT /users/<id>',
                'delete': 'DELETE /users/<id>'
            },
            'orders': {
                'list': 'GET /orders',
                'get': 'GET /orders/<id>',
                'user_orders': 'GET /orders/user/<user_id>',
                'create': 'POST /orders',
                'update': 'PUT /orders/<id>',
                'update_status': 'PATCH /orders/<id>/status',
                'delete': 'DELETE /orders/<id>'
            },
            'combined': {
                'user_with_orders': 'GET /users/<id>/orders',
                'order_with_user': 'GET /orders/<id>/details'
            },
            'health': 'GET /health',
            'stats': 'GET /stats'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health():
    users_health, users_status = service_client.make_request(
        'GET',
        f"{USERS_SERVICE_URL}/health"
    )
    
    orders_health, orders_status = service_client.make_request(
        'GET',
        f"{ORDERS_SERVICE_URL}/health"
    )
    
    all_healthy = (users_status == 200 and orders_status == 200)
    overall_status = 'healthy' if all_healthy else 'degraded'
    
    return jsonify({
        'status': overall_status,
        'gateway': 'healthy',
        'services': {
            'users': {
                'status': 'healthy' if users_status == 200 else 'unhealthy',
                'url': USERS_SERVICE_URL
            },
            'orders': {
                'status': 'healthy' if orders_status == 200 else 'unhealthy',
                'url': ORDERS_SERVICE_URL
            }
        },
        'timestamp': datetime.now().isoformat()
    }), 200 if all_healthy else 503


@app.route('/stats', methods=['GET'])
def stats():
    users_stats, _ = service_client.make_request(
        'GET',
        f"{USERS_SERVICE_URL}/stats"
    )
    
    orders_stats, _ = service_client.make_request(
        'GET',
        f"{ORDERS_SERVICE_URL}/stats"
    )
    
    return jsonify({
        'gateway': {
            'total_requests': STATS['total_requests'],
            'users_requests': STATS['users_requests'],
            'orders_requests': STATS['orders_requests'],
            'errors': STATS['errors']
        },
        'services': {
            'users': users_stats if users_stats else {'error': 'unavailable'},
            'orders': orders_stats if orders_stats else {'error': 'unavailable'}
        },
        'timestamp': datetime.now().isoformat()
    })



@app.route('/users', methods=['GET'])
def get_users():
    STATS['users_requests'] += 1
    
    params = request.args.to_dict()
    
    data, status_code = service_client.make_request(
        'GET',
        f"{USERS_SERVICE_URL}/users",
        params=params
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    STATS['users_requests'] += 1
    
    data, status_code = service_client.make_request(
        'GET',
        f"{USERS_SERVICE_URL}/users/{user_id}"
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/users', methods=['POST'])
def create_user():
    STATS['users_requests'] += 1
    
    data, status_code = service_client.make_request(
        'POST',
        f"{USERS_SERVICE_URL}/users",
        json=request.get_json()
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    STATS['users_requests'] += 1
    
    data, status_code = service_client.make_request(
        'PUT',
        f"{USERS_SERVICE_URL}/users/{user_id}",
        json=request.get_json()
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    STATS['users_requests'] += 1
    
    data, status_code = service_client.make_request(
        'DELETE',
        f"{USERS_SERVICE_URL}/users/{user_id}"
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/orders', methods=['GET'])
def get_orders():
    STATS['orders_requests'] += 1
    
    params = request.args.to_dict()
    
    data, status_code = service_client.make_request(
        'GET',
        f"{ORDERS_SERVICE_URL}/orders",
        params=params
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    STATS['orders_requests'] += 1
    
    data, status_code = service_client.make_request(
        'GET',
        f"{ORDERS_SERVICE_URL}/orders/{order_id}"
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    STATS['orders_requests'] += 1
    
    data, status_code = service_client.make_request(
        'GET',
        f"{ORDERS_SERVICE_URL}/orders/user/{user_id}"
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/orders', methods=['POST'])
def create_order():
    STATS['orders_requests'] += 1
    
    data, status_code = service_client.make_request(
        'POST',
        f"{ORDERS_SERVICE_URL}/orders",
        json=request.get_json()
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    STATS['orders_requests'] += 1
    
    data, status_code = service_client.make_request(
        'PUT',
        f"{ORDERS_SERVICE_URL}/orders/{order_id}",
        json=request.get_json()
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/orders/<int:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    STATS['orders_requests'] += 1
    
    data, status_code = service_client.make_request(
        'PATCH',
        f"{ORDERS_SERVICE_URL}/orders/{order_id}/status",
        json=request.get_json()
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    STATS['orders_requests'] += 1
    
    data, status_code = service_client.make_request(
        'DELETE',
        f"{ORDERS_SERVICE_URL}/orders/{order_id}"
    )
    
    if status_code >= 400:
        STATS['errors'] += 1
    
    return jsonify(data), status_code


@app.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_with_orders(user_id):
    STATS['users_requests'] += 1
    STATS['orders_requests'] += 1
    
    user_data, user_status = service_client.make_request(
        'GET',
        f"{USERS_SERVICE_URL}/users/{user_id}"
    )
    
    if user_status != 200:
        STATS['errors'] += 1
        return jsonify(user_data), user_status
    
    orders_data, orders_status = service_client.make_request(
        'GET',
        f"{ORDERS_SERVICE_URL}/orders/user/{user_id}"
    )
    
    if orders_status != 200:
        STATS['errors'] += 1
        user_data['orders'] = {'error': 'Could not fetch orders'}  # type: ignore
    else:
        user_data['orders'] = orders_data # type: ignore
    
    return jsonify(user_data), 200


@app.route('/orders/<int:order_id>/details', methods=['GET'])
def get_order_with_user(order_id):
    STATS['orders_requests'] += 1
    STATS['users_requests'] += 1
    
    order_data, order_status = service_client.make_request(
        'GET',
        f"{ORDERS_SERVICE_URL}/orders/{order_id}"
    )
    
    if order_status != 200:
        STATS['errors'] += 1
        return jsonify(order_data), order_status
    
    order = order_data.get('order', {}) # type: ignore
    user_id = order.get('user_id')
    
    if not user_id:
        return jsonify(order_data), 200
    
    user_data, user_status = service_client.make_request(
        'GET',
        f"{USERS_SERVICE_URL}/users/{user_id}"
    )
    
    if user_status != 200:
        STATS['errors'] += 1
        order_data['user'] = {'error': 'Could not fetch user'} # type: ignore
    else:
        order_data['user'] = user_data.get('user', {}) # type: ignore
    
    return jsonify(order_data), 200


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting API Gateway")
    logger.info(f"Users Service: {USERS_SERVICE_URL}")
    logger.info(f"Orders Service: {ORDERS_SERVICE_URL}")
    logger.info("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False
    )
