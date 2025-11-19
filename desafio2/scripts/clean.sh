#!/bin/bash

# Script para limpeza completa do ambiente

set -e

echo "=========================================="
echo "  Limpeza Completa - Desafio 2"
echo "=========================================="
echo ""

echo "⚠️  ATENÇÃO: Este script irá remover:"
echo "   - Todos os containers"
echo "   - Todas as imagens"
echo "   - Todos os volumes (DADOS SERÃO PERDIDOS)"
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
docker compose down -v

echo ""
echo "🗑️  Removendo imagens..."
docker rmi desafio2-app desafio2-reader 2>/dev/null || true

echo ""
echo "🌐 Removendo rede..."
docker network rm desafio2-network 2>/dev/null || true

echo ""
echo "✅ Ambiente limpo completamente!"
