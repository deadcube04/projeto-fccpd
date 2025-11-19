#!/bin/bash

# Script para testar a API

echo "=========================================="
echo "  Testando API - Desafio 2"
echo "=========================================="
echo ""

BASE_URL="http://localhost:5000"

# 1. Testa endpoint raiz
echo "1️⃣ Testando endpoint raiz (/)..."
echo ""
curl -s $BASE_URL | python3 -m json.tool
echo ""
echo ""

# 2. Testa health check
echo "2️⃣ Testando health check..."
echo ""
curl -s $BASE_URL/health | python3 -m json.tool
echo ""
echo ""

# 3. Lista tarefas
echo "3️⃣ Listando tarefas..."
echo ""
curl -s $BASE_URL/tasks | python3 -m json.tool
echo ""
echo ""

# 4. Obtém estatísticas
echo "4️⃣ Obtendo estatísticas..."
echo ""
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "✅ Testes concluídos!"
echo "=========================================="
