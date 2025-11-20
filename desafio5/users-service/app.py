from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import logging
import random

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

USERS_DB = {}

STATS = {
    'total_requests': 0,
    'users_created': 0,
    'start_time': datetime.now().isoformat()
}


def initialize_sample_data():
    sample_users = [
        {
            'id': 1,
            'name': 'Alice Silva',
            'email': 'alice.silva@email.com',
            'phone': '+55 11 98765-4321',
            'address': {
                'street': 'Rua das Flores, 123',
                'city': 'São Paulo',
                'state': 'SP',
                'zip': '01234-567'
            },
            'created_at': (datetime.now() - timedelta(days=365)).isoformat(),
            'status': 'active'
        },
        {
            'id': 2,
            'name': 'Bruno Costa',
            'email': 'bruno.costa@email.com',
            'phone': '+55 21 99876-5432',
            'address': {
                'street': 'Av. Atlântica, 456',
                'city': 'Rio de Janeiro',
                'state': 'RJ',
                'zip': '22011-010'
            },
            'created_at': (datetime.now() - timedelta(days=180)).isoformat(),
            'status': 'active'
        },
        {
            'id': 3,
            'name': 'Carla Mendes',
            'email': 'carla.mendes@email.com',
            'phone': '+55 31 98765-1234',
            'address': {
                'street': 'Rua da Bahia, 789',
                'city': 'Belo Horizonte',
                'state': 'MG',
                'zip': '30160-011'
            },
            'created_at': (datetime.now() - timedelta(days=90)).isoformat(),
            'status': 'active'
        },
        {
            'id': 4,
            'name': 'Daniel Souza',
            'email': 'daniel.souza@email.com',
            'phone': '+55 85 99123-4567',
            'address': {
                'street': 'Av. Beira Mar, 321',
                'city': 'Fortaleza',
                'state': 'CE',
                'zip': '60165-121'
            },
            'created_at': (datetime.now() - timedelta(days=45)).isoformat(),
            'status': 'active'
        },
        {
            'id': 5,
            'name': 'Elena Santos',
            'email': 'elena.santos@email.com',
            'phone': '+55 51 98234-5678',
            'address': {
                'street': 'Rua dos Andradas, 654',
                'city': 'Porto Alegre',
                'state': 'RS',
                'zip': '90020-001'
            },
            'created_at': (datetime.now() - timedelta(days=200)).isoformat(),
            'status': 'inactive'
        }
    ]
    
    for user in sample_users:
        USERS_DB[user['id']] = user
    
    logger.info(f"Initialized database with {len(sample_users)} users")


@app.before_request
def before_request():
    STATS['total_requests'] += 1
    logger.info(f"{request.method} {request.path} - Client: {request.remote_addr}")


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'Users Service',
        'version': '1.0.0',
        'description': 'Microsserviço de gerenciamento de usuários',
        'endpoints': {
            'list_users': 'GET /users',
            'get_user': 'GET /users/<id>',
            'create_user': 'POST /users',
            'update_user': 'PUT /users/<id>',
            'delete_user': 'DELETE /users/<id>',
            'health': 'GET /health',
            'stats': 'GET /stats'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Users Service',
        'total_users': len(USERS_DB),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/stats', methods=['GET'])
def stats():
    active_users = sum(1 for u in USERS_DB.values() if u['status'] == 'active')
    
    return jsonify({
        'service': 'Users Service',
        'requests': STATS['total_requests'],
        'users_created': STATS['users_created'],
        'users': {
            'total': len(USERS_DB),
            'active': active_users,
            'inactive': len(USERS_DB) - active_users
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/users', methods=['GET'])
def get_users():
    status_filter = request.args.get('status')
    
    users = list(USERS_DB.values())
    
    if status_filter:
        users = [u for u in users if u['status'] == status_filter]
    
    return jsonify({
        'total': len(users),
        'users': users,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = USERS_DB.get(user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'user_id': user_id
        }), 404
    
    return jsonify({
        'user': user,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['name', 'email', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    user_id = max(USERS_DB.keys()) + 1 if USERS_DB else 1
    
    new_user = {
        'id': user_id,
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'address': data.get('address', {}),
        'created_at': datetime.now().isoformat(),
        'status': 'active'
    }
    
    USERS_DB[user_id] = new_user
    STATS['users_created'] += 1
    
    logger.info(f"Created user {user_id}: {new_user['name']}")
    
    return jsonify({
        'message': 'User created successfully',
        'user': new_user
    }), 201


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = USERS_DB.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    updatable_fields = ['name', 'email', 'phone', 'address', 'status']
    for field in updatable_fields:
        if field in data:
            user[field] = data[field]
    
    logger.info(f"Updated user {user_id}: {user['name']}")
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user
    })


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = USERS_DB.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user['status'] = 'inactive'
    
    logger.info(f"Deleted user {user_id}: {user['name']}")
    
    return jsonify({
        'message': 'User deleted successfully',
        'user_id': user_id
    })


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Users Service")
    logger.info("=" * 60)
    
    initialize_sample_data()
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False
    )
