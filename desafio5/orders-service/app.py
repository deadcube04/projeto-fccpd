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

ORDERS_DB = {}

STATS = {
    'total_requests': 0,
    'orders_created': 0,
    'start_time': datetime.now().isoformat()
}

ORDER_STATUSES = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']


def initialize_sample_data():
    sample_orders = [
        {
            'id': 1,
            'user_id': 1,
            'items': [
                {'product': 'Notebook Dell', 'quantity': 1, 'price': 3499.00},
                {'product': 'Mouse Logitech', 'quantity': 1, 'price': 89.90}
            ],
            'total': 3588.90,
            'status': 'delivered',
            'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
            'updated_at': (datetime.now() - timedelta(days=25)).isoformat(),
            'shipping_address': {
                'street': 'Rua das Flores, 123',
                'city': 'São Paulo',
                'state': 'SP',
                'zip': '01234-567'
            }
        },
        {
            'id': 2,
            'user_id': 2,
            'items': [
                {'product': 'iPhone 15', 'quantity': 1, 'price': 5999.00},
                {'product': 'Capinha', 'quantity': 1, 'price': 49.90}
            ],
            'total': 6048.90,
            'status': 'shipped',
            'created_at': (datetime.now() - timedelta(days=5)).isoformat(),
            'updated_at': (datetime.now() - timedelta(days=2)).isoformat(),
            'shipping_address': {
                'street': 'Av. Atlântica, 456',
                'city': 'Rio de Janeiro',
                'state': 'RJ',
                'zip': '22011-010'
            }
        },
        {
            'id': 3,
            'user_id': 1,
            'items': [
                {'product': 'Teclado Mecânico', 'quantity': 1, 'price': 450.00}
            ],
            'total': 450.00,
            'status': 'processing',
            'created_at': (datetime.now() - timedelta(days=2)).isoformat(),
            'updated_at': (datetime.now() - timedelta(days=1)).isoformat(),
            'shipping_address': {
                'street': 'Rua das Flores, 123',
                'city': 'São Paulo',
                'state': 'SP',
                'zip': '01234-567'
            }
        },
        {
            'id': 4,
            'user_id': 3,
            'items': [
                {'product': 'Cadeira Gamer', 'quantity': 1, 'price': 1299.00},
                {'product': 'Mousepad', 'quantity': 1, 'price': 79.90}
            ],
            'total': 1378.90,
            'status': 'pending',
            'created_at': (datetime.now() - timedelta(hours=12)).isoformat(),
            'updated_at': (datetime.now() - timedelta(hours=12)).isoformat(),
            'shipping_address': {
                'street': 'Rua da Bahia, 789',
                'city': 'Belo Horizonte',
                'state': 'MG',
                'zip': '30160-011'
            }
        },
        {
            'id': 5,
            'user_id': 4,
            'items': [
                {'product': 'Monitor LG 27"', 'quantity': 2, 'price': 899.00}
            ],
            'total': 1798.00,
            'status': 'delivered',
            'created_at': (datetime.now() - timedelta(days=45)).isoformat(),
            'updated_at': (datetime.now() - timedelta(days=40)).isoformat(),
            'shipping_address': {
                'street': 'Av. Beira Mar, 321',
                'city': 'Fortaleza',
                'state': 'CE',
                'zip': '60165-121'
            }
        },
        {
            'id': 6,
            'user_id': 2,
            'items': [
                {'product': 'Webcam Logitech', 'quantity': 1, 'price': 399.00}
            ],
            'total': 399.00,
            'status': 'cancelled',
            'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
            'updated_at': (datetime.now() - timedelta(days=9)).isoformat(),
            'shipping_address': {
                'street': 'Av. Atlântica, 456',
                'city': 'Rio de Janeiro',
                'state': 'RJ',
                'zip': '22011-010'
            }
        }
    ]
    
    for order in sample_orders:
        ORDERS_DB[order['id']] = order
    
    logger.info(f"Initialized database with {len(sample_orders)} orders")


@app.before_request
def before_request():
    STATS['total_requests'] += 1
    logger.info(f"{request.method} {request.path} - Client: {request.remote_addr}")


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'Orders Service',
        'version': '1.0.0',
        'description': 'Microsserviço de gerenciamento de pedidos',
        'endpoints': {
            'list_orders': 'GET /orders',
            'get_order': 'GET /orders/<id>',
            'get_user_orders': 'GET /orders/user/<user_id>',
            'create_order': 'POST /orders',
            'update_order': 'PUT /orders/<id>',
            'update_status': 'PATCH /orders/<id>/status',
            'delete_order': 'DELETE /orders/<id>',
            'health': 'GET /health',
            'stats': 'GET /stats'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Orders Service',
        'total_orders': len(ORDERS_DB),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/stats', methods=['GET'])
def stats():
    status_count = {}
    total_value = 0.0
    
    for order in ORDERS_DB.values():
        status = order['status']
        status_count[status] = status_count.get(status, 0) + 1
        total_value += order['total']
    
    return jsonify({
        'service': 'Orders Service',
        'requests': STATS['total_requests'],
        'orders_created': STATS['orders_created'],
        'orders': {
            'total': len(ORDERS_DB),
            'by_status': status_count,
            'total_value': round(total_value, 2)
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/orders', methods=['GET'])
def get_orders():
    status_filter = request.args.get('status')
    user_id_filter = request.args.get('user_id')
    
    orders = list(ORDERS_DB.values())
    
    if status_filter:
        orders = [o for o in orders if o['status'] == status_filter]
    
    if user_id_filter:
        user_id = int(user_id_filter)
        orders = [o for o in orders if o['user_id'] == user_id]
    
    return jsonify({
        'total': len(orders),
        'orders': orders,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = ORDERS_DB.get(order_id)
    
    if not order:
        return jsonify({
            'error': 'Order not found',
            'order_id': order_id
        }), 404
    
    return jsonify({
        'order': order,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    user_orders = [o for o in ORDERS_DB.values() if o['user_id'] == user_id]
    
    return jsonify({
        'user_id': user_id,
        'total': len(user_orders),
        'orders': user_orders,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['user_id', 'items']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    if not isinstance(data['items'], list) or len(data['items']) == 0:
        return jsonify({'error': 'Items must be a non-empty list'}), 400
    
    total = 0.0
    for item in data['items']:
        if 'price' not in item or 'quantity' not in item:
            return jsonify({'error': 'Each item must have price and quantity'}), 400
        total += item['price'] * item['quantity']
    
    order_id = max(ORDERS_DB.keys()) + 1 if ORDERS_DB else 1
    
    new_order = {
        'id': order_id,
        'user_id': data['user_id'],
        'items': data['items'],
        'total': round(total, 2),
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'shipping_address': data.get('shipping_address', {})
    }
    
    ORDERS_DB[order_id] = new_order
    STATS['orders_created'] += 1
    
    logger.info(f"Created order {order_id} for user {data['user_id']}")
    
    return jsonify({
        'message': 'Order created successfully',
        'order': new_order
    }), 201


@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = ORDERS_DB.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'items' in data:
        order['items'] = data['items']
        total = sum(item['price'] * item['quantity'] for item in data['items'])
        order['total'] = round(total, 2)
    
    if 'status' in data and data['status'] in ORDER_STATUSES:
        order['status'] = data['status']
    
    if 'shipping_address' in data:
        order['shipping_address'] = data['shipping_address']
    
    order['updated_at'] = datetime.now().isoformat()
    
    logger.info(f"Updated order {order_id}")
    
    return jsonify({
        'message': 'Order updated successfully',
        'order': order
    })


@app.route('/orders/<int:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    order = ORDERS_DB.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    new_status = data['status']
    if new_status not in ORDER_STATUSES:
        return jsonify({
            'error': 'Invalid status',
            'valid_statuses': ORDER_STATUSES
        }), 400
    
    old_status = order['status']
    order['status'] = new_status
    order['updated_at'] = datetime.now().isoformat()
    
    logger.info(f"Updated order {order_id} status: {old_status} -> {new_status}")
    
    return jsonify({
        'message': 'Order status updated successfully',
        'order': order
    })


@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = ORDERS_DB.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    order['status'] = 'cancelled'
    order['updated_at'] = datetime.now().isoformat()
    
    logger.info(f"Cancelled order {order_id}")
    
    return jsonify({
        'message': 'Order cancelled successfully',
        'order_id': order_id
    })


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Orders Service")
    logger.info("=" * 60)
    
    initialize_sample_data()
    
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=False
    )
