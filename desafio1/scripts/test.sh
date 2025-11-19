#!/bin/bash

# Script para testar a comunicação entre containers

echo "=========================================="
echo "  Testando Comunicação"
echo "=========================================="
echo ""

# Testa requisição direta ao servidor
echo "1️⃣ Testando requisição HTTP ao servidor (localhost:8080)..."
echo ""
curl -s http://localhost:8080 | python3 -m json.tool
echo ""
echo ""

# Testa health check
echo "2️⃣ Testando health check..."
echo ""
curl -s http://localhost:8080/health | python3 -m json.tool
echo ""
echo ""

# Testa estatísticas
echo "3️⃣ Testando endpoint de estatísticas..."
echo ""
curl -s http://localhost:8080/stats | python3 -m json.tool
echo ""
echo ""

# Testa requisição de dentro do container cliente
echo "4️⃣ Testando requisição de dentro do container cliente..."
echo ""
docker exec desafio1-client wget -qO- http://server:8080 | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "✅ Testes concluídos!"
echo "=========================================="
