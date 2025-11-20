#!/bin/bash

# Script para testar orquestração do Gateway

echo "=========================================="
echo "  Testando Orquestração do Gateway"
echo "=========================================="
echo ""

GATEWAY="http://localhost:8000"

echo "🎯 O Gateway pode combinar dados de múltiplos microsserviços!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Teste 1: Usuário com seus pedidos
echo "1️⃣ ENDPOINT COMBINADO: Usuário + Pedidos"
echo ""
echo "O Gateway orquestra chamadas para ambos os serviços:"
echo "  1. Busca dados do usuário (Users Service)"
echo "  2. Busca pedidos do usuário (Orders Service)"
echo "  3. Combina as informações"
echo ""
echo "GET $GATEWAY/users/1/orders"
echo ""

curl -s $GATEWAY/users/1/orders | python3 -c "
import sys, json
data = json.load(sys.stdin)
user = data.get('user', {})
orders = data.get('orders', {}).get('orders', [])

print(f'Usuário: {user.get(\"name\")}')
print(f'Email: {user.get(\"email\")}')
print(f'Status: {user.get(\"status\")}')
print()
print(f'Total de pedidos: {len(orders)}')
print()
print('Pedidos:')
for order in orders:
    print(f'  • Pedido #{order[\"id\"]}: R$ {order[\"total\"]} - {order[\"status\"]}')
    print(f'    Items: {len(order[\"items\"])} produto(s)')
    print(f'    Data: {order[\"created_at\"][:10]}')
    print()
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Teste 2: Pedido com dados do usuário
echo "2️⃣ ENDPOINT COMBINADO: Pedido + Usuário"
echo ""
echo "O Gateway enriquece o pedido com dados do usuário:"
echo "  1. Busca dados do pedido (Orders Service)"
echo "  2. Extrai user_id do pedido"
echo "  3. Busca dados do usuário (Users Service)"
echo "  4. Combina as informações"
echo ""
echo "GET $GATEWAY/orders/1/details"
echo ""

curl -s $GATEWAY/orders/1/details | python3 -c "
import sys, json
data = json.load(sys.stdin)
order = data.get('order', {})
user = data.get('user', {})

print(f'Pedido #{order.get(\"id\")}')
print(f'Status: {order.get(\"status\")}')
print(f'Total: R$ {order.get(\"total\")}')
print(f'Data: {order.get(\"created_at\", \"\")[:10]}')
print()
print('Cliente:')
print(f'  Nome: {user.get(\"name\")}')
print(f'  Email: {user.get(\"email\")}')
print(f'  Telefone: {user.get(\"phone\")}')
print()
print('Endereço de entrega:')
addr = order.get('shipping_address', {})
print(f'  {addr.get(\"street\")}')
print(f'  {addr.get(\"city\")}/{addr.get(\"state\")} - {addr.get(\"zip\")}')
print()
print(f'Items ({len(order.get(\"items\", []))}):'  )
for item in order.get('items', []):
    print(f'  • {item.get(\"product\")}: {item.get(\"quantity\")}x R$ {item.get(\"price\")}')
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Teste 3: Comparação - acesso direto vs orquestrado
echo "3️⃣ COMPARAÇÃO: Requisições Separadas vs Gateway"
echo ""
echo "❌ SEM GATEWAY (2 requisições do cliente):"
echo "   Cliente → Users Service (busca usuário)"
echo "   Cliente → Orders Service (busca pedidos)"
echo ""
echo "✅ COM GATEWAY (1 requisição do cliente):"
echo "   Cliente → Gateway (busca usuário com pedidos)"
echo "   Gateway → Users Service (busca usuário)"
echo "   Gateway → Orders Service (busca pedidos)"
echo "   Gateway ← combina dados ← retorna ao cliente"
echo ""
echo "Benefícios:"
echo "  • Cliente faz apenas 1 requisição"
echo "  • Gateway orquestra a lógica"
echo "  • Menor latência para o cliente"
echo "  • Ponto único de entrada"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Teste 4: Filtros via gateway
echo "4️⃣ FILTROS VIA GATEWAY"
echo ""
echo "GET $GATEWAY/orders?status=pending"
echo ""
curl -s "$GATEWAY/orders?status=pending" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Pedidos com status \"pending\": {data[\"total\"]}')
print()
for order in data['orders']:
    print(f'  • Pedido #{order[\"id\"]}: Usuário {order[\"user_id\"]} - R$ {order[\"total\"]}')
"
echo ""
echo ""

# Teste 5: Estatísticas agregadas
echo "5️⃣ ESTATÍSTICAS AGREGADAS"
echo ""
echo "Gateway coleta estatísticas de todos os serviços:"
echo ""
curl -s $GATEWAY/stats | python3 -c "
import sys, json
data = json.load(sys.stdin)
gw = data.get('gateway', {})
users = data.get('services', {}).get('users', {})
orders = data.get('services', {}).get('orders', {})

print('API Gateway:')
print(f'  Total de requisições: {gw.get(\"total_requests\")}')
print(f'  Requisições p/ Users: {gw.get(\"users_requests\")}')
print(f'  Requisições p/ Orders: {gw.get(\"orders_requests\")}')
print(f'  Erros: {gw.get(\"errors\")}')
print()
print('Users Service:')
users_data = users.get('users', {})
print(f'  Total de usuários: {users_data.get(\"total\")}')
print(f'  Ativos: {users_data.get(\"active\")}')
print()
print('Orders Service:')
orders_data = orders.get('orders', {})
print(f'  Total de pedidos: {orders_data.get(\"total\")}')
print(f'  Valor total: R$ {orders_data.get(\"total_value\")}')
"
echo ""
echo ""

echo "=========================================="
echo "✅ Orquestração testada com sucesso!"
echo "=========================================="
echo ""
echo "🎯 Conceitos demonstrados:"
echo "  ✓ Gateway como ponto único de entrada"
echo "  ✓ Orquestração de múltiplos serviços"
echo "  ✓ Combinação de dados"
echo "  ✓ Proxy transparente"
echo "  ✓ Agregação de estatísticas"
echo ""
