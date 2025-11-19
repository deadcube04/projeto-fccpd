#!/bin/bash

# Script para testar todos os endpoints

echo "=========================================="
echo "  Testando Endpoints"
echo "=========================================="
echo ""

SERVICE_A="http://localhost:5000"
SERVICE_B="http://localhost:5001"

echo "═══════════════════════════════════════"
echo "  SERVICE A - USERS SERVICE"
echo "═══════════════════════════════════════"
echo ""

# Service A - Root
echo "1️⃣ GET $SERVICE_A/"
curl -s $SERVICE_A/ | python3 -m json.tool
echo ""
echo ""

# Service A - Lista usuários
echo "2️⃣ GET $SERVICE_A/users"
curl -s $SERVICE_A/users | python3 -m json.tool | head -40
echo "  ... (output truncado)"
echo ""
echo ""

# Service A - Busca usuário específico
echo "3️⃣ GET $SERVICE_A/users/1"
curl -s $SERVICE_A/users/1 | python3 -m json.tool
echo ""
echo ""

# Service A - Health check
echo "4️⃣ GET $SERVICE_A/health"
curl -s $SERVICE_A/health | python3 -m json.tool
echo ""
echo ""

# Service A - Estatísticas
echo "5️⃣ GET $SERVICE_A/stats"
curl -s $SERVICE_A/stats | python3 -m json.tool
echo ""
echo ""

echo "═══════════════════════════════════════"
echo "  SERVICE B - PROFILE SERVICE"
echo "═══════════════════════════════════════"
echo ""

# Service B - Root
echo "6️⃣ GET $SERVICE_B/"
curl -s $SERVICE_B/ | python3 -m json.tool
echo ""
echo ""

# Service B - Lista perfis
echo "7️⃣ GET $SERVICE_B/profiles"
curl -s $SERVICE_B/profiles | python3 -m json.tool | head -50
echo "  ... (output truncado)"
echo ""
echo ""

# Service B - Busca perfil específico
echo "8️⃣ GET $SERVICE_B/profiles/2"
curl -s $SERVICE_B/profiles/2 | python3 -m json.tool
echo ""
echo ""

# Service B - Resumo executivo
echo "9️⃣ GET $SERVICE_B/profiles/3/summary"
curl -s $SERVICE_B/profiles/3/summary | python3 -m json.tool
echo ""
echo ""

# Service B - Health check
echo "🔟 GET $SERVICE_B/health"
curl -s $SERVICE_B/health | python3 -m json.tool
echo ""
echo ""

# Service B - Estatísticas
echo "1️⃣1️⃣ GET $SERVICE_B/stats"
curl -s $SERVICE_B/stats | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "✅ Testes concluídos!"
echo "=========================================="
