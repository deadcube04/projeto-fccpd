#!/bin/bash

# Script para iniciar o Desafio 3 - Docker Compose Orquestrando Serviços

set -e

echo "=========================================="
echo "  Desafio 3 - Docker Compose"
echo "=========================================="
echo ""

# Verifica Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    exit 1
fi

# Verifica Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não está instalado!"
    exit 1
fi

echo "✓ Docker e Docker Compose encontrados"
echo ""

# Limpa containers antigos (mantém volumes)
echo "🧹 Limpando containers antigos..."
docker compose down 2>/dev/null || true
echo ""

# Constrói as imagens
echo "🔨 Construindo imagens Docker..."
docker compose build --no-cache
echo ""

# Inicia todos os serviços
echo "🚀 Iniciando serviços..."
docker compose up -d
echo ""

# Aguarda PostgreSQL ficar healthy
echo "⏳ Aguardando PostgreSQL..."
for i in {1..30}; do
    if docker inspect desafio3-postgres --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ PostgreSQL está healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Aguarda Redis ficar healthy
echo "⏳ Aguardando Redis..."
for i in {1..30}; do
    if docker inspect desafio3-redis --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ Redis está healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Aguarda aplicação ficar healthy
echo "⏳ Aguardando aplicação web..."
for i in {1..30}; do
    if docker inspect desafio3-web --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ Aplicação web está healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""
echo ""

# Status dos serviços
echo "📊 Status dos serviços:"
docker compose ps
echo ""

# Informações da rede
echo "🌐 Rede Docker:"
docker network inspect desafio3-network --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}' 2>/dev/null
echo ""

# Informações dos volumes
echo "💾 Volumes persistentes:"
docker volume ls | grep desafio3
echo ""

echo "=========================================="
echo "✅ Ambiente iniciado com sucesso!"
echo "=========================================="
echo ""
echo "📝 Serviços disponíveis:"
echo "  - API Gateway:     http://localhost:8000"
echo "  - PostgreSQL:      localhost:5432"
echo "  - Redis:           localhost:6379"
echo ""
echo "📝 Comandos úteis:"
echo "  - Ver logs:                 docker compose logs -f"
echo "  - Testar API:               ./scripts/test.sh"
echo "  - Popular produtos:         ./scripts/populate.sh"
echo "  - Testar comunicação:       ./scripts/test_communication.sh"
echo "  - Demonstrar cache:         ./scripts/demo_cache.sh"
echo "  - Estatísticas:             curl http://localhost:8000/stats"
echo "  - Status dos serviços:      curl http://localhost:8000/services"
echo "  - Parar serviços:           docker compose down"
echo ""
