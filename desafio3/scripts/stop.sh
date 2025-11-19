#!/bin/bash

# Script para parar os serviços

set -e

echo "=========================================="
echo "  Parando Desafio 3"
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
