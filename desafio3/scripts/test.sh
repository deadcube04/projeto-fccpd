#!/bin/bash

# Script para testar a API

echo "=========================================="
echo "  Testando API - Desafio 3"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

# 1. Testa endpoint raiz
echo "1️⃣ Testando endpoint raiz (/)..."
echo ""
curl -s $BASE_URL | python3 -m json.tool
echo ""
echo ""

# 2. Testa health check de todos os serviços
echo "2️⃣ Testando health check..."
echo ""
curl -s $BASE_URL/health | python3 -m json.tool
echo ""
echo ""

# 3. Testa status detalhado dos serviços
echo "3️⃣ Testando status dos serviços..."
echo ""
curl -s $BASE_URL/services | python3 -m json.tool
echo ""
echo ""

# 4. Lista produtos
echo "4️⃣ Listando produtos..."
echo ""
curl -s $BASE_URL/products | python3 -m json.tool
echo ""
echo ""

# 5. Obtém estatísticas
echo "5️⃣ Obtendo estatísticas..."
echo ""
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "✅ Testes concluídos!"
echo "=========================================="
