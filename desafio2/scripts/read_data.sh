#!/bin/bash

# Script para executar o leitor de dados

echo "=========================================="
echo "  Lendo Dados Persistidos"
echo "=========================================="
echo ""

# Executa o container leitor
docker compose run --rm reader

echo ""
