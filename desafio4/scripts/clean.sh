#!/bin/bash

# Script para limpeza completa

set -e

echo "=========================================="
echo "  Limpeza Completa - Desafio 4"
echo "=========================================="
echo ""

echo "⚠️  ATENÇÃO: Este script irá remover:"
echo "   - Todos os containers"
echo "   - Todas as imagens"
echo "   - Rede Docker"
echo ""
read -p "Deseja continuar? (s/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operação cancelada."
    exit 0
fi

echo ""
echo "🧹 Parando e removendo containers..."
docker compose down

echo ""
echo "🗑️  Removendo imagens..."
docker rmi desafio4-service-a desafio4-service-b 2>/dev/null || true

echo ""
echo "🌐 Removendo rede..."
docker network rm desafio4-network 2>/dev/null || true

echo ""
echo "✅ Ambiente limpo completamente!"
