#!/bin/bash

# Script para visualizar logs

echo "=========================================="
echo "  Logs do Desafio 4"
echo "=========================================="
echo ""
echo "Pressione Ctrl+C para sair"
echo ""

docker compose logs -f --tail=50
