#!/bin/bash

# Script para visualizar logs do Desafio 1

echo "=========================================="
echo "  Logs do Desafio 1"
echo "=========================================="
echo ""
echo "Pressione Ctrl+C para sair"
echo ""

# Mostra logs de ambos containers em tempo real
docker compose logs -f --tail=50
