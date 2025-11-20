#!/bin/bash

# Script para visualizar logs

echo "=========================================="
echo "  Logs do Desafio 5"
echo "=========================================="
echo ""
echo "Pressione Ctrl+C para sair"
echo ""

docker compose logs -f --tail=50
