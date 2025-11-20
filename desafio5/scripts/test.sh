#!/bin/bash

# Script para testar o API Gateway

echo "=========================================="
echo "  Testando API Gateway"
echo "=========================================="
echo ""

GATEWAY="http://localhost:8000"

# 1. Informações do gateway
echo "1️⃣ Informações do API Gateway"
echo ""
echo "GET $GATEWAY/"
curl -s $GATEWAY/ | python3 -m json.tool | head -40
echo ""
echo ""

# 2. Health check
echo "2️⃣ Health Check (Gateway + Microsserviços)"
echo ""
echo "GET $GATEWAY/health"
curl -s $GATEWAY/health | python3 -m json.tool
echo ""
echo ""

# 3. Estatísticas
echo "3️⃣ Estatísticas do Gateway"
echo ""
echo "GET $GATEWAY/stats"
curl -s $GATEWAY/stats | python3 -m json.tool
echo ""
echo ""

echo "═══════════════════════════════════════"
echo "  TESTANDO ENDPOINTS DE USUÁRIOS"
echo "═══════════════════════════════════════"
echo ""

# 4. Lista usuários
echo "4️⃣ Listar Usuários (via Gateway)"
echo ""
echo "GET $GATEWAY/users"
curl -s $GATEWAY/users | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total: {data[\"total\"]} usuários')
print()
for user in data['users'][:3]:
    print(f'  • ID {user[\"id\"]}: {user[\"name\"]} ({user[\"email\"]})')
"
echo ""
echo ""

# 5. Busca usuário específico
echo "5️⃣ Buscar Usuário Específico"
echo ""
echo "GET $GATEWAY/users/1"
curl -s $GATEWAY/users/1 | python3 -m json.tool
echo ""
echo ""

echo "═══════════════════════════════════════"
echo "  TESTANDO ENDPOINTS DE PEDIDOS"
echo "═══════════════════════════════════════"
echo ""

# 6. Lista pedidos
echo "6️⃣ Listar Pedidos (via Gateway)"
echo ""
echo "GET $GATEWAY/orders"
curl -s $GATEWAY/orders | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total: {data[\"total\"]} pedidos')
print()
for order in data['orders'][:3]:
    print(f'  • Pedido #{order[\"id\"]}: Usuário {order[\"user_id\"]} - R$ {order[\"total\"]} ({order[\"status\"]})')
"
echo ""
echo ""

# 7. Busca pedido específico
echo "7️⃣ Buscar Pedido Específico"
echo ""
echo "GET $GATEWAY/orders/1"
curl -s $GATEWAY/orders/1 | python3 -m json.tool
echo ""
echo ""

# 8. Busca pedidos de um usuário
echo "8️⃣ Buscar Pedidos de um Usuário"
echo ""
echo "GET $GATEWAY/orders/user/1"
curl -s $GATEWAY/orders/user/1 | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Usuário {data[\"user_id\"]}: {data[\"total\"]} pedidos')
print()
for order in data['orders']:
    print(f'  • Pedido #{order[\"id\"]}: R$ {order[\"total\"]} - {order[\"status\"]}')
"
echo ""
echo ""

echo "=========================================="
echo "✅ Testes básicos concluídos!"
echo "=========================================="
echo ""
echo "💡 Para testar orquestração de dados:"
echo "   ./scripts/test_orchestration.sh"
echo ""
