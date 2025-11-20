from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import requests
import logging
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

USERS_SERVICE_URL = "http://service-a:5000"

STATS = {
    'total_requests': 0,
    'profiles_generated': 0,
    'service_a_calls': 0,
    'service_a_errors': 0,
    'start_time': datetime.now().isoformat()
}


class UsersServiceClient:
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ProfileService/1.0',
            'Accept': 'application/json'
        })
    
    def get_all_users(self, filters: Optional[Dict] = None) -> Optional[Dict]:
        """
        Busca todos os usuários do Service A
        
        Args:
            filters: Filtros opcionais (active, department, role)
            
        Returns:
            Dicionário com resposta ou None em caso de erro
        """
        try:
            url = f"{self.base_url}/users"
            STATS['service_a_calls'] += 1
            
            response = self.session.get(url, params=filters or {}, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched {data.get('total', 0)} users from Service A")
            return data
            
        except requests.exceptions.RequestException as e:
            STATS['service_a_errors'] += 1
            logger.error(f"Error fetching users from Service A: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Busca usuário específico do Service A
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com usuário ou None em caso de erro
        """
        try:
            url = f"{self.base_url}/users/{user_id}"
            STATS['service_a_calls'] += 1
            
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched user {user_id} from Service A")
            return data.get('user')
            
        except requests.exceptions.RequestException as e:
            STATS['service_a_errors'] += 1
            logger.error(f"Error fetching user {user_id} from Service A: {e}")
            return None
    
    def check_health(self) -> bool:
        """
        Verifica se Service A está disponível
        
        Returns:
            True se disponível, False caso contrário
        """
        try:
            url = f"{self.base_url}/health"
            response = self.session.get(url, timeout=3)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


# Inicializa cliente
users_client = UsersServiceClient(USERS_SERVICE_URL)


# ============================================================================
# FUNÇÕES DE ENRIQUECIMENTO DE PERFIL
# ============================================================================

def calculate_experience_level(registration_date: str) -> str:
    """
    Calcula nível de experiência baseado na data de registro
    
    Args:
        registration_date: Data de registro (ISO format)
        
    Returns:
        Nível de experiência (Junior/Mid/Senior/Expert)
    """
    try:
        reg_date = datetime.fromisoformat(registration_date)
        days_active = (datetime.now() - reg_date).days
        
        if days_active < 180:
            return "Junior"
        elif days_active < 365:
            return "Mid-Level"
        elif days_active < 730:
            return "Senior"
        else:
            return "Expert"
    except Exception:
        return "Unknown"


def calculate_activity_status(last_login: str, active: bool) -> Dict:
    """
    Calcula status de atividade do usuário
    
    Args:
        last_login: Data do último login (ISO format)
        active: Se usuário está ativo
        
    Returns:
        Dicionário com informações de atividade
    """
    if not active:
        return {
            'status': 'Inactive',
            'description': 'Account deactivated',
            'last_seen': 'N/A'
        }
    
    try:
        login_date = datetime.fromisoformat(last_login)
        hours_since_login = (datetime.now() - login_date).total_seconds() / 3600
        
        if hours_since_login < 1:
            status = 'Online'
            description = 'Active right now'
        elif hours_since_login < 24:
            status = 'Recently Active'
            description = f'Last seen {int(hours_since_login)} hours ago'
        elif hours_since_login < 168:  # 7 days
            days = int(hours_since_login / 24)
            status = 'Active This Week'
            description = f'Last seen {days} day{"s" if days > 1 else ""} ago'
        else:
            days = int(hours_since_login / 24)
            status = 'Inactive'
            description = f'Last seen {days} days ago'
        
        return {
            'status': status,
            'description': description,
            'last_seen': login_date.strftime('%Y-%m-%d %H:%M')
        }
    except Exception:
        return {
            'status': 'Unknown',
            'description': 'Unable to determine activity',
            'last_seen': 'N/A'
        }


def enrich_user_profile(user: Dict) -> Dict:
    """
    Enriquece perfil do usuário com informações adicionais
    
    Args:
        user: Dados básicos do usuário do Service A
        
    Returns:
        Perfil enriquecido com informações combinadas
    """
    STATS['profiles_generated'] += 1
    
    # Calcula informações adicionais
    experience_level = calculate_experience_level(user.get('registration_date', ''))
    activity = calculate_activity_status(user.get('last_login', ''), user.get('active', False))
    
    # Calcula tempo na plataforma
    try:
        reg_date = datetime.fromisoformat(user.get('registration_date', ''))
        days_active = (datetime.now() - reg_date).days
        years = days_active // 365
        months = (days_active % 365) // 30
    except Exception:
        years, months = 0, 0
    
    # Monta perfil enriquecido
    enriched_profile = {
        # Dados básicos do usuário (Service A)
        'user_id': user.get('id'),
        'username': user.get('username'),
        'full_name': user.get('full_name'),
        'email': user.get('email'),
        
        # Informações profissionais
        'professional': {
            'role': user.get('role'),
            'department': user.get('department'),
            'experience_level': experience_level,
            'skills': user.get('skills', []),
            'projects': user.get('projects', []),
            'location': user.get('location')
        },
        
        # Informações de atividade
        'activity': activity,
        
        # Métricas calculadas
        'metrics': {
            'member_since': user.get('registration_date', '').split('T')[0],
            'tenure': f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}",
            'total_projects': len(user.get('projects', [])),
            'skill_count': len(user.get('skills', [])),
            'account_status': 'Active' if user.get('active') else 'Inactive'
        },
        
        # Metadata
        'profile_generated_at': datetime.now().isoformat(),
        'data_source': 'Users Service (Microservice A)'
    }
    
    return enriched_profile


def generate_profile_summary(profile: Dict) -> Dict:
    """
    Gera resumo executivo do perfil
    
    Args:
        profile: Perfil enriquecido
        
    Returns:
        Resumo executivo formatado
    """
    username = profile.get('username', 'Unknown')
    full_name = profile.get('full_name', 'Unknown')
    role = profile['professional'].get('role', 'Unknown')
    dept = profile['professional'].get('department', 'Unknown')
    exp_level = profile['professional'].get('experience_level', 'Unknown')
    tenure = profile['metrics'].get('tenure', 'Unknown')
    activity_desc = profile['activity'].get('description', 'Unknown')
    
    # Gera descrição textual
    summary_text = (
        f"{full_name} (@{username}) is a {exp_level} {role} in the {dept} department. "
        f"They have been with the company for {tenure}. {activity_desc}."
    )
    
    # Adiciona informações de projetos e skills
    projects = profile['professional'].get('projects', [])
    skills = profile['professional'].get('skills', [])
    
    if projects:
        summary_text += f" Currently working on: {', '.join(projects[:3])}."
    
    if skills:
        summary_text += f" Key skills: {', '.join(skills[:5])}."
    
    return {
        'user_id': profile.get('user_id'),
        'summary': summary_text,
        'highlights': {
            'name': full_name,
            'role': role,
            'experience': exp_level,
            'activity': profile['activity'].get('status'),
            'projects_count': len(projects),
            'skills_count': len(skills)
        },
        'generated_at': datetime.now().isoformat()
    }


# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.before_request
def before_request():
    """Executa antes de cada requisição"""
    STATS['total_requests'] += 1
    logger.info(f"{request.method} {request.path} - Client: {request.remote_addr}")


# ============================================================================
# ENDPOINTS - INFORMAÇÕES DO SERVIÇO
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Informações básicas do serviço"""
    return jsonify({
        'service': 'Profile Service (Microservice B)',
        'version': '1.0.0',
        'description': 'API REST que enriquece dados de usuários consumindo o Users Service',
        'depends_on': 'Users Service (Microservice A) at ' + USERS_SERVICE_URL,
        'endpoints': {
            'profiles': '/profiles',
            'profile_detail': '/profiles/<id>',
            'profile_summary': '/profiles/<id>/summary',
            'health': '/health',
            'stats': '/stats'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check do serviço e dependências"""
    service_a_healthy = users_client.check_health()
    
    uptime = (datetime.now() - datetime.fromisoformat(STATS['start_time'])).total_seconds()
    
    overall_status = 'healthy' if service_a_healthy else 'degraded'
    
    return jsonify({
        'status': overall_status,
        'service': 'Profile Service',
        'uptime_seconds': round(uptime, 2),
        'dependencies': {
            'users_service': {
                'status': 'available' if service_a_healthy else 'unavailable',
                'url': USERS_SERVICE_URL
            }
        },
        'timestamp': datetime.now().isoformat()
    }), 200 if service_a_healthy else 503


@app.route('/stats', methods=['GET'])
def stats():
    """Estatísticas detalhadas do serviço"""
    uptime = (datetime.now() - datetime.fromisoformat(STATS['start_time'])).total_seconds()
    
    # Calcula taxa de erro
    total_calls = STATS['service_a_calls']
    error_rate = (STATS['service_a_errors'] / total_calls * 100) if total_calls > 0 else 0
    
    return jsonify({
        'service': 'Profile Service',
        'uptime_seconds': round(uptime, 2),
        'requests': {
            'total': STATS['total_requests'],
            'profiles_generated': STATS['profiles_generated']
        },
        'service_a_communication': {
            'total_calls': STATS['service_a_calls'],
            'errors': STATS['service_a_errors'],
            'error_rate_percent': round(error_rate, 2),
            'url': USERS_SERVICE_URL
        },
        'timestamp': datetime.now().isoformat()
    })


# ============================================================================
# ENDPOINTS - PERFIS ENRIQUECIDOS
# ============================================================================

@app.route('/profiles', methods=['GET'])
def get_profiles():
    """
    Lista perfis enriquecidos de todos os usuários
    
    Query Parameters:
        active (bool): Filtra por status ativo/inativo
        department (str): Filtra por departamento
        role (str): Filtra por cargo
    """
    # Obtém filtros da query string
    filters = {}
    if request.args.get('active'):
        filters['active'] = request.args.get('active')
    if request.args.get('department'):
        filters['department'] = request.args.get('department')
    if request.args.get('role'):
        filters['role'] = request.args.get('role')
    
    # Busca usuários do Service A
    response = users_client.get_all_users(filters)
    
    if not response:
        return jsonify({
            'error': 'Unable to fetch users from Users Service',
            'service_a_url': USERS_SERVICE_URL
        }), 503
    
    users = response.get('users', [])
    
    # Enriquece cada perfil
    enriched_profiles = [enrich_user_profile(user) for user in users]
    
    logger.info(f"Generated {len(enriched_profiles)} enriched profiles")
    
    return jsonify({
        'total': len(enriched_profiles),
        'profiles': enriched_profiles,
        'filters_applied': filters,
        'data_source': 'Users Service (Microservice A)',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/profiles/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """Busca perfil enriquecido de usuário específico"""
    # Busca usuário do Service A
    user = users_client.get_user_by_id(user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found or service unavailable',
            'user_id': user_id,
            'service_a_url': USERS_SERVICE_URL
        }), 404
    
    # Enriquece perfil
    enriched_profile = enrich_user_profile(user)
    
    logger.info(f"Generated enriched profile for user {user_id}")
    
    return jsonify({
        'profile': enriched_profile,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/profiles/<int:user_id>/summary', methods=['GET'])
def get_profile_summary(user_id):
    """
    Busca resumo executivo do perfil do usuário
    
    Retorna uma descrição textual formatada combinando informações do Service A
    com análises calculadas pelo Service B.
    """
    # Busca usuário do Service A
    user = users_client.get_user_by_id(user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found or service unavailable',
            'user_id': user_id
        }), 404
    
    # Enriquece perfil e gera resumo
    enriched_profile = enrich_user_profile(user)
    summary = generate_profile_summary(enriched_profile)
    
    logger.info(f"Generated summary for user {user_id}")
    
    return jsonify(summary)


# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Profile Service (Microservice B)")
    logger.info(f"Users Service URL: {USERS_SERVICE_URL}")
    logger.info("=" * 60)
    
    # Inicia servidor
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False
    )
