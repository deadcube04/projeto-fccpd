#!/bin/bash

# Script para demonstrar funcionamento do cache

set -e

echo "=========================================="
echo "  DEMONSTRAÇÃO DE CACHE (Redis)"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

# Limpa cache
echo "🧹 Limpando cache..."
curl -s $BASE_URL/cache/clear | python3 -m json.tool
echo ""
echo ""

# Primeira requisição (MISS - busca do banco)
echo "1️⃣ PRIMEIRA REQUISIÇÃO (Cache MISS - busca do banco)..."
echo ""
echo "⏱️  Medindo tempo de resposta..."
time curl -s $BASE_URL/products > /dev/null
echo ""
curl -s $BASE_URL/products | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"  Fonte: {data['source']}\")"
echo ""
echo ""

# Segunda requisição (HIT - busca do cache)
echo "2️⃣ SEGUNDA REQUISIÇÃO (Cache HIT - busca do cache)..."
echo ""
echo "⏱️  Medindo tempo de resposta..."
time curl -s $BASE_URL/products > /dev/null
echo ""
curl -s $BASE_URL/products | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"  Fonte: {data['source']}\")"
echo ""
echo ""

# Comparação
echo "📊 COMPARAÇÃO:"
echo "  • Cache MISS (primeira requisição): busca no PostgreSQL (mais lento)"
echo "  • Cache HIT (segunda requisição): busca no Redis (muito mais rápido)"
echo ""
echo ""

# Testa produto específico
echo "3️⃣ Testando cache de produto específico..."
echo ""
echo "Primeira busca (MISS):"
curl -s $BASE_URL/products/1 | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"  Fonte: {data.get('source', 'N/A')}\")" 2>/dev/null || echo "  Produto ainda não existe"
echo ""
echo "Segunda busca (HIT):"
curl -s $BASE_URL/products/1 | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"  Fonte: {data.get('source', 'N/A')}\")" 2>/dev/null || echo "  Produto ainda não existe"
echo ""
echo ""

# Mostra estatísticas
echo "4️⃣ Estatísticas de cache:"
echo ""
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""
echo ""

# Testa invalidação de cache
echo "5️⃣ Testando invalidação de cache ao criar produto..."
echo ""
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Produto Teste Cache",
    "price": 99.99,
    "category": "test"
  }' | python3 -m json.tool
echo ""
echo "Cache foi invalidado automaticamente!"
echo ""
echo "Próxima requisição será MISS novamente:"
curl -s $BASE_URL/products | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"  Fonte: {data['source']}\")"
echo ""
echo ""

echo "=========================================="
echo "✅ Demonstração de cache concluída!"
echo "=========================================="
echo ""
echo "🎯 Principais conceitos demonstrados:"
echo "  • Cache MISS: Dados buscados do PostgreSQL"
echo "  • Cache HIT: Dados buscados do Redis (mais rápido)"
echo "  • Cache TTL: Tempo de expiração configurável"
echo "  • Cache Invalidation: Limpa cache ao modificar dados"
echo "  • Performance: Redis é muito mais rápido que PostgreSQL"
echo ""
