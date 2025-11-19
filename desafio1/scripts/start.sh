#!/bin/bash

# Script para iniciar o Desafio 1 - Containers em Rede
# Este script constrói e inicia os containers Docker

set -e  # Sai em caso de erro

echo "=========================================="
echo "  Desafio 1 - Containers em Rede"
echo "=========================================="
echo ""

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    echo "Por favor, instale o Docker antes de continuar."
    exit 1
fi

# Verifica se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não está instalado!"
    echo "Por favor, instale o Docker Compose antes de continuar."
    exit 1
fi

echo "✓ Docker e Docker Compose encontrados"
echo ""

# Remove containers antigos se existirem
echo "🧹 Limpando containers antigos..."
docker compose down -v 2>/dev/null || true
echo ""

# Constrói as imagens
echo "🔨 Construindo imagens Docker..."
docker compose build --no-cache
echo ""

# Inicia os containers
echo "🚀 Iniciando containers..."
docker compose up -d
echo ""

# Aguarda o servidor estar healthy
echo "⏳ Aguardando servidor ficar healthy..."
for i in {1..30}; do
    if docker inspect desafio1-server --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ Servidor está healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""
echo ""

# Aguarda o cliente iniciar
echo "⏳ Aguardando cliente iniciar..."
sleep 3
echo ""

# Verifica status dos containers
echo "📊 Status dos containers:"
docker compose ps
echo ""

# Mostra informações da rede
echo "🌐 Informações da rede customizada:"
docker network inspect desafio1-network --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}' 2>/dev/null
echo ""

echo "=========================================="
echo "✅ Containers iniciados com sucesso!"
echo "=========================================="
echo ""
echo "📝 Comandos úteis:"
echo "  - Ver logs do servidor:  docker compose logs -f server"
echo "  - Ver logs do cliente:   docker compose logs -f client"
echo "  - Ver todos os logs:     docker compose logs -f"
echo "  - Parar containers:      docker compose stop"
echo "  - Remover containers:    docker compose down"
echo ""
echo "🌐 Acesse o servidor em: http://localhost:8080"
echo ""
