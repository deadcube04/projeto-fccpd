#!/bin/bash

# Script para parar os serviços

set -e

echo "=========================================="
echo "  Parando Desafio 5"
echo "=========================================="
echo ""

echo "🛑 Parando containers..."
docker compose down

echo ""
echo "✅ Containers parados!"
echo ""
