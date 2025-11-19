#!/bin/bash

# Script para parar o Desafio 1 - Containers em Rede

set -e

echo "=========================================="
echo "  Parando Desafio 1"
echo "=========================================="
echo ""

echo "🛑 Parando containers..."
docker compose down

echo ""
echo "✅ Containers parados com sucesso!"
