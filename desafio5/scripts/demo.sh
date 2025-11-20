#!/bin/bash

# Script de demonstração completa

echo "=========================================="
echo "  DEMONSTRAÇÃO COMPLETA"
echo "  API Gateway com Microsserviços"
echo "=========================================="
echo ""

GATEWAY="http://localhost:8000"

echo "🎯 Arquitetura: API Gateway + 2 Microsserviços"
echo ""
echo "   ┌─────────────┐"
echo "   │   Cliente   │"
echo "   └──────┬──────┘"
echo "          │"
echo "          │ HTTP (porta 8000)"
echo "          ▼"
echo "   ┌─────────────────┐"
echo "   │  API Gateway    │ ◄── Ponto único de entrada"
echo "   └────┬───────┬────┘"
echo "        │       │"
echo "        │       │ HTTP interno"
echo "        ▼       ▼"
echo "   ┌────────┐ ┌────────┐"
echo "   │ Users  │ │ Orders │"
echo "   │Service │ │Service │"
echo "   └────────┘ └────────┘"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cenário 1: Criar novo usuário
echo "📋 CENÁRIO 1: Criar Novo Usuário"
echo ""
echo "Cliente faz requisição ao Gateway:"
echo "POST $GATEWAY/users"
echo ""

NEW_USER=$(curl -s -X POST $GATEWAY/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fernanda Lima",
    "email": "fernanda.lima@email.com",
    "phone": "+55 48 99234-5678",
    "address": {
      "street": "Rua das Palmeiras, 100",
      "city": "Florianópolis",
      "state": "SC",
      "zip": "88010-000"
    }
  }')

echo "$NEW_USER" | python3 -c "
import sys, json
data = json.load(sys.stdin)
user = data.get('user', {})
print(f'✓ Usuário criado com sucesso!')
print(f'  ID: {user.get(\"id\")}')
print(f'  Nome: {user.get(\"name\")}')
print(f'  Email: {user.get(\"email\")}')
"
echo ""
NEW_USER_ID=$(echo "$NEW_USER" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])")
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cenário 2: Criar pedido para o usuário
echo "📦 CENÁRIO 2: Criar Pedido para o Usuário"
echo ""
echo "POST $GATEWAY/orders"
echo ""

NEW_ORDER=$(curl -s -X POST $GATEWAY/orders \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $NEW_USER_ID,
    \"items\": [
      {\"product\": \"Notebook Acer\", \"quantity\": 1, \"price\": 2799.00},
      {\"product\": \"Mouse Wireless\", \"quantity\": 1, \"price\": 59.90}
    ],
    \"shipping_address\": {
      \"street\": \"Rua das Palmeiras, 100\",
      \"city\": \"Florianópolis\",
      \"state\": \"SC\",
      \"zip\": \"88010-000\"
    }
  }")

echo "$NEW_ORDER" | python3 -c "
import sys, json
data = json.load(sys.stdin)
order = data.get('order', {})
print(f'✓ Pedido criado com sucesso!')
print(f'  Pedido ID: {order.get(\"id\")}')
print(f'  Usuário ID: {order.get(\"user_id\")}')
print(f'  Total: R$ {order.get(\"total\")}')
print(f'  Status: {order.get(\"status\")}')
"
echo ""
NEW_ORDER_ID=$(echo "$NEW_ORDER" | python3 -c "import sys, json; print(json.load(sys.stdin)['order']['id'])")
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cenário 3: Buscar usuário com pedidos (orquestração)
echo "🔍 CENÁRIO 3: Buscar Usuário com Seus Pedidos"
echo ""
echo "Gateway orquestra: Users Service + Orders Service"
echo "GET $GATEWAY/users/$NEW_USER_ID/orders"
echo ""

curl -s $GATEWAY/users/$NEW_USER_ID/orders | python3 -c "
import sys, json
data = json.load(sys.stdin)
user = data.get('user', {})
orders = data.get('orders', {}).get('orders', [])

print('Cliente:')
print(f'  {user.get(\"name\")} ({user.get(\"email\")})')
print()
print(f'Pedidos: {len(orders)}')
for order in orders:
    print(f'  • Pedido #{order[\"id\"]}: R$ {order[\"total\"]} - {order[\"status\"]}')
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cenário 4: Atualizar status do pedido
echo "📝 CENÁRIO 4: Atualizar Status do Pedido"
echo ""
echo "PATCH $GATEWAY/orders/$NEW_ORDER_ID/status"
echo ""

curl -s -X PATCH $GATEWAY/orders/$NEW_ORDER_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status": "processing"}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
order = data.get('order', {})
print(f'✓ Status atualizado!')
print(f'  Pedido #{order.get(\"id\")}')
print(f'  Novo status: {order.get(\"status\")}')
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cenário 5: Buscar pedido com detalhes do usuário
echo "📊 CENÁRIO 5: Pedido com Detalhes do Usuário"
echo ""
echo "Gateway combina: Order + User"
echo "GET $GATEWAY/orders/$NEW_ORDER_ID/details"
echo ""

curl -s $GATEWAY/orders/$NEW_ORDER_ID/details | python3 -c "
import sys, json
data = json.load(sys.stdin)
order = data.get('order', {})
user = data.get('user', {})

print(f'Pedido #{order.get(\"id\")} - {order.get(\"status\").upper()}')
print()
print('Cliente:')
print(f'  Nome: {user.get(\"name\")}')
print(f'  Email: {user.get(\"email\")}')
print(f'  Telefone: {user.get(\"phone\")}')
print()
print('Endereço:')
addr = order.get('shipping_address', {})
print(f'  {addr.get(\"street\")}')
print(f'  {addr.get(\"city\")}/{addr.get(\"state\")} - {addr.get(\"zip\")}')
print()
print(f'Total: R$ {order.get(\"total\")}')
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cenário 6: Listar pedidos pendentes
echo "📑 CENÁRIO 6: Listar Pedidos Pendentes"
echo ""
echo "GET $GATEWAY/orders?status=pending"
echo ""

curl -s "$GATEWAY/orders?status=pending" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total de pedidos pendentes: {data[\"total\"]}')
print()
for order in data['orders']:
    print(f'  • Pedido #{order[\"id\"]}')
    print(f'    Usuário: {order[\"user_id\"]}')
    print(f'    Valor: R$ {order[\"total\"]}')
    print(f'    Criado: {order[\"created_at\"][:10]}')
    print()
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cenário 7: Estatísticas finais
echo "📊 CENÁRIO 7: Estatísticas do Sistema"
echo ""

curl -s $GATEWAY/stats | python3 -c "
import sys, json
data = json.load(sys.stdin)
gw = data.get('gateway', {})
users = data.get('services', {}).get('users', {}).get('users', {})
orders = data.get('services', {}).get('orders', {}).get('orders', {})

print('=== API GATEWAY ===')
print(f'Total de requisições: {gw.get(\"total_requests\")}')
print(f'  → Users Service: {gw.get(\"users_requests\")}')
print(f'  → Orders Service: {gw.get(\"orders_requests\")}')
print(f'Erros: {gw.get(\"errors\")}')
print()
print('=== USERS SERVICE ===')
print(f'Total de usuários: {users.get(\"total\")}')
print(f'Ativos: {users.get(\"active\")}')
print()
print('=== ORDERS SERVICE ===')
print(f'Total de pedidos: {orders.get(\"total\")}')
by_status = orders.get('by_status', {})
print('Por status:')
for status, count in by_status.items():
    print(f'  • {status}: {count}')
print(f'Valor total: R$ {orders.get(\"total_value\")}')
"
echo ""
echo ""

echo "=========================================="
echo "✅ Demonstração Completa Concluída!"
echo "=========================================="
echo ""
echo "🎯 Conceitos demonstrados:"
echo "  ✓ Gateway como ponto único de entrada"
echo "  ✓ Orquestração de microsserviços"
echo "  ✓ Criação de recursos via Gateway"
echo "  ✓ Combinação de dados (orquestração)"
echo "  ✓ Filtros e consultas"
echo "  ✓ Atualização de recursos"
echo "  ✓ Agregação de estatísticas"
echo ""
echo "🏗️ Fluxo demonstrado:"
echo "  1. Criar usuário via Gateway"
echo "  2. Criar pedido para o usuário"
echo "  3. Buscar usuário com pedidos (orquestrado)"
echo "  4. Atualizar status do pedido"
echo "  5. Buscar pedido com dados do usuário"
echo "  6. Filtrar pedidos por status"
echo "  7. Visualizar estatísticas agregadas"
echo ""
