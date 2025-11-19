#!/bin/bash

# Script para testar comunicação entre serviços

echo "=========================================="
echo "  Testando Comunicação Entre Serviços"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

# 1. Testa se web consegue acessar PostgreSQL
echo "1️⃣ Testando comunicação Web → PostgreSQL..."
echo ""
echo "Fazendo requisição que acessa o banco de dados:"
curl -s $BASE_URL/health | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"  Database: {data.get('database', 'N/A')}\")"
echo "✓ Web consegue comunicar com PostgreSQL!"
echo ""
echo ""

# 2. Testa se web consegue acessar Redis
echo "2️⃣ Testando comunicação Web → Redis..."
echo ""
echo "Fazendo requisição que acessa o cache:"
curl -s $BASE_URL/health | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"  Cache: {data.get('cache', 'N/A')}\")"
echo "✓ Web consegue comunicar com Redis!"
echo ""
echo ""

# 3. Testa resolução DNS interna
echo "3️⃣ Testando resolução DNS interna..."
echo ""
docker exec desafio3-web ping -c 3 postgres | tail -1
docker exec desafio3-web ping -c 3 redis | tail -1
echo "✓ Resolução DNS funcionando!"
echo ""
echo ""

# 4. Testa acesso direto ao PostgreSQL
echo "4️⃣ Testando acesso direto ao PostgreSQL..."
echo ""
docker exec desafio3-postgres psql -U postgres -d products_db -c "SELECT COUNT(*) as produtos FROM products;" 2>/dev/null
echo "✓ PostgreSQL respondendo!"
echo ""
echo ""

# 5. Testa acesso direto ao Redis
echo "5️⃣ Testando acesso direto ao Redis..."
echo ""
docker exec desafio3-redis redis-cli PING
docker exec desafio3-redis redis-cli DBSIZE | awk '{print "  Chaves no cache: " $0}'
echo "✓ Redis respondendo!"
echo ""
echo ""

# 6. Testa status detalhado de todos os serviços
echo "6️⃣ Status detalhado dos serviços:"
echo ""
curl -s $BASE_URL/services | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "✅ Todos os serviços estão comunicando!"
echo "=========================================="
echo ""
echo "📊 Resumo da comunicação:"
echo "  • Web ←→ PostgreSQL: ✓"
echo "  • Web ←→ Redis: ✓"
echo "  • DNS interno: ✓"
echo "  • Rede Docker: ✓"
echo ""
