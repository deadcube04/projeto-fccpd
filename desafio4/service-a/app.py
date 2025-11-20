from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import logging
import random
import uuid

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
    'users_updated': 0,
    'start_time': datetime.now().isoformat()
}


def initialize_sample_data():
    sample_users = [
        {
            'id': 1,
            'username': 'alice_dev',
            'email': 'alice@example.com',
            'full_name': 'Alice Developer',
            'role': 'Senior Developer',
            'department': 'Engineering',
            'active': True,
            'registration_date': (datetime.now() - timedelta(days=730)).isoformat(),
            'last_login': (datetime.now() - timedelta(hours=2)).isoformat(),
            'projects': ['Project Alpha', 'Project Beta'],
            'skills': ['Python', 'Docker', 'Kubernetes'],
            'location': 'San Francisco, CA'
        },
        {
            'id': 2,
            'username': 'bob_ops',
            'email': 'bob@example.com',
            'full_name': 'Bob Operations',
            'role': 'DevOps Engineer',
            'department': 'Operations',
            'active': True,
            'registration_date': (datetime.now() - timedelta(days=365)).isoformat(),
            'last_login': (datetime.now() - timedelta(hours=5)).isoformat(),
            'projects': ['Infrastructure', 'CI/CD Pipeline'],
            'skills': ['AWS', 'Terraform', 'Ansible'],
            'location': 'New York, NY'
        },
        {
            'id': 3,
            'username': 'charlie_data',
            'email': 'charlie@example.com',
            'full_name': 'Charlie Data',
            'role': 'Data Scientist',
            'department': 'Analytics',
            'active': True,
            'registration_date': (datetime.now() - timedelta(days=180)).isoformat(),
            'last_login': (datetime.now() - timedelta(hours=1)).isoformat(),
            'projects': ['ML Pipeline', 'Data Warehouse'],
            'skills': ['Python', 'TensorFlow', 'SQL'],
            'location': 'Austin, TX'
        },
        {
            'id': 4,
            'username': 'diana_design',
            'email': 'diana@example.com',
            'full_name': 'Diana Designer',
            'role': 'UX Designer',
            'department': 'Product',
            'active': True,
            'registration_date': (datetime.now() - timedelta(days=90)).isoformat(),
            'last_login': (datetime.now() - timedelta(hours=3)).isoformat(),
            'projects': ['Mobile App', 'Web Redesign'],
            'skills': ['Figma', 'Adobe XD', 'User Research'],
            'location': 'Seattle, WA'
        },
        {
            'id': 5,
            'username': 'eve_manager',
            'email': 'eve@example.com',
            'full_name': 'Eve Manager',
            'role': 'Product Manager',
            'department': 'Product',
            'active': True,
            'registration_date': (datetime.now() - timedelta(days=450)).isoformat(),
            'last_login': (datetime.now() - timedelta(hours=6)).isoformat(),
            'projects': ['Roadmap 2024', 'Feature Planning'],
            'skills': ['Agile', 'Jira', 'Stakeholder Management'],
            'location': 'Boston, MA'
        },
        {
            'id': 6,
            'username': 'frank_qa',
            'email': 'frank@example.com',
            'full_name': 'Frank Quality',
            'role': 'QA Engineer',
            'department': 'Engineering',
            'active': False,
            'registration_date': (datetime.now() - timedelta(days=600)).isoformat(),
            'last_login': (datetime.now() - timedelta(days=30)).isoformat(),
            'projects': ['Test Automation'],
            'skills': ['Selenium', 'Pytest', 'API Testing'],
            'location': 'Chicago, IL'
        }
    ]
    
    for user in sample_users:
        USERS_DB[user['id']] = user
    
    logger.info(f"Initialized database with {len(sample_users)} sample users")


@app.before_request
def before_request():
    STATS['total_requests'] += 1
    logger.info(f"{request.method} {request.path} - Client: {request.remote_addr}")


def get_next_user_id():
    """Gera próximo ID disponível para novo usuário"""
    if not USERS_DB:
        return 1
    return max(USERS_DB.keys()) + 1


def validate_user_data(data, is_update=False):
    """
    Valida dados de usuário
    
    Args:
        data: Dicionário com dados do usuário
        is_update: Se True, permite campos opcionais
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['username', 'email', 'full_name', 'role']
    
    if not is_update:
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
    
    # Valida email
    if 'email' in data and '@' not in data['email']:
        return False, "Invalid email format"
    
    # Valida username único
    if 'username' in data and not is_update:
        for user in USERS_DB.values():
            if user['username'] == data['username']:
                return False, f"Username '{data['username']}' already exists"
    
    return True, None


# ============================================================================
# ENDPOINTS - INFORMAÇÕES DO SERVIÇO
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Informações básicas do serviço"""
    return jsonify({
        'service': 'Users Service (Microservice A)',
        'version': '1.0.0',
        'description': 'API REST para gerenciamento de usuários',
        'endpoints': {
            'users': '/users',
            'user_detail': '/users/<id>',
            'health': '/health',
            'stats': '/stats'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check do serviço"""
    uptime = (datetime.now() - datetime.fromisoformat(STATS['start_time'])).total_seconds()
    
    return jsonify({
        'status': 'healthy',
        'service': 'Users Service',
        'uptime_seconds': round(uptime, 2),
        'total_users': len(USERS_DB),
        'active_users': sum(1 for u in USERS_DB.values() if u['active']),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/stats', methods=['GET'])
def stats():
    """Estatísticas detalhadas do serviço"""
    uptime = (datetime.now() - datetime.fromisoformat(STATS['start_time'])).total_seconds()
    
    # Calcula estatísticas
    total_users = len(USERS_DB)
    active_users = sum(1 for u in USERS_DB.values() if u['active'])
    
    departments = {}
    roles = {}
    for user in USERS_DB.values():
        dept = user.get('department', 'Unknown')
        role = user.get('role', 'Unknown')
        departments[dept] = departments.get(dept, 0) + 1
        roles[role] = roles.get(role, 0) + 1
    
    return jsonify({
        'service': 'Users Service',
        'uptime_seconds': round(uptime, 2),
        'requests': {
            'total': STATS['total_requests'],
            'users_created': STATS['users_created'],
            'users_updated': STATS['users_updated']
        },
        'users': {
            'total': total_users,
            'active': active_users,
            'inactive': total_users - active_users,
            'by_department': departments,
            'by_role': roles
        },
        'timestamp': datetime.now().isoformat()
    })


# ============================================================================
# ENDPOINTS - CRUD DE USUÁRIOS
# ============================================================================

@app.route('/users', methods=['GET'])
def get_users():
    """
    Lista todos os usuários
    
    Query Parameters:
        active (bool): Filtra por status ativo/inativo
        department (str): Filtra por departamento
        role (str): Filtra por cargo
    """
    # Obtém filtros
    active_filter = request.args.get('active')
    department_filter = request.args.get('department')
    role_filter = request.args.get('role')
    
    # Aplica filtros
    users = list(USERS_DB.values())
    
    if active_filter is not None:
        active_bool = active_filter.lower() == 'true'
        users = [u for u in users if u['active'] == active_bool]
    
    if department_filter:
        users = [u for u in users if u.get('department', '').lower() == department_filter.lower()]
    
    if role_filter:
        users = [u for u in users if u.get('role', '').lower() == role_filter.lower()]
    
    logger.info(f"Returning {len(users)} users (filters: active={active_filter}, dept={department_filter}, role={role_filter})")
    
    return jsonify({
        'total': len(users),
        'users': users,
        'filters_applied': {
            'active': active_filter,
            'department': department_filter,
            'role': role_filter
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = USERS_DB.get(user_id)
    
    if not user:
        logger.warning(f"User {user_id} not found")
        return jsonify({
            'error': 'User not found',
            'user_id': user_id
        }), 404
    
    logger.info(f"Returning user {user_id}: {user['username']}")
    
    return jsonify({
        'user': user,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/users', methods=['POST'])
def create_user():
    """
    Cria novo usuário
    
    Body (JSON):
        username (str): Nome de usuário (único)
        email (str): Email do usuário
        full_name (str): Nome completo
        role (str): Cargo
        department (str, optional): Departamento
        skills (list, optional): Lista de habilidades
        location (str, optional): Localização
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Valida dados
    is_valid, error_msg = validate_user_data(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Cria novo usuário
    user_id = get_next_user_id()
    new_user = {
        'id': user_id,
        'username': data['username'],
        'email': data['email'],
        'full_name': data['full_name'],
        'role': data['role'],
        'department': data.get('department', 'General'),
        'active': True,
        'registration_date': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat(),
        'projects': data.get('projects', []),
        'skills': data.get('skills', []),
        'location': data.get('location', 'Remote')
    }
    
    USERS_DB[user_id] = new_user
    STATS['users_created'] += 1
    
    logger.info(f"Created user {user_id}: {new_user['username']}")
    
    return jsonify({
        'message': 'User created successfully',
        'user': new_user
    }), 201


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Atualiza usuário existente
    
    Body (JSON): Campos a serem atualizados
    """
    user = USERS_DB.get(user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'user_id': user_id
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Valida dados
    is_valid, error_msg = validate_user_data(data, is_update=True)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Atualiza campos permitidos
    updatable_fields = [
        'email', 'full_name', 'role', 'department', 
        'active', 'projects', 'skills', 'location'
    ]
    
    for field in updatable_fields:
        if field in data:
            user[field] = data[field]
    
    user['last_login'] = datetime.now().isoformat()
    STATS['users_updated'] += 1
    
    logger.info(f"Updated user {user_id}: {user['username']}")
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user
    })


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = USERS_DB.get(user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'user_id': user_id
        }), 404
    
    # Soft delete - apenas marca como inativo
    user['active'] = False
    
    logger.info(f"Deactivated user {user_id}: {user['username']}")
    
    return jsonify({
        'message': 'User deactivated successfully',
        'user_id': user_id
    })


# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Users Service (Microservice A)")
    logger.info("=" * 60)
    
    # Inicializa dados de exemplo
    initialize_sample_data()
    
    # Inicia servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
