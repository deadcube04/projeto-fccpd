#!/bin/bash

# Script para limpar completamente o ambiente do Desafio 1

set -e

echo "=========================================="
echo "  Limpeza Completa - Desafio 1"
echo "=========================================="
echo ""

echo "🧹 Parando e removendo containers..."
docker compose down -v

echo ""
echo "🗑️  Removendo imagens..."
docker rmi desafio1-server desafio1-client 2>/dev/null || true

echo ""
echo "🌐 Removendo rede..."
docker network rm desafio1-network 2>/dev/null || true

echo ""
echo "✅ Ambiente limpo com sucesso!"
