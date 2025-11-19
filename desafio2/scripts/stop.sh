#!/bin/bash

# Script para parar o Desafio 2

set -e

echo "=========================================="
echo "  Parando Desafio 2"
echo "=========================================="
echo ""

echo "🛑 Parando containers (mantendo volumes)..."
docker compose down

echo ""
echo "✅ Containers parados!"
echo ""
echo "💡 Nota: Os volumes foram mantidos."
echo "   Para remover tudo incluindo volumes, use:"
echo "   docker compose down -v"
echo ""
