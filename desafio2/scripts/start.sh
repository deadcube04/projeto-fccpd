#!/bin/bash

# Script para iniciar o Desafio 2 - Volumes e Persistência

set -e

echo "=========================================="
echo "  Desafio 2 - Volumes e Persistência"
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
echo "🧹 Limpando containers antigos (mantendo volumes)..."
docker compose down 2>/dev/null || true
echo ""

# Constrói as imagens
echo "🔨 Construindo imagens Docker..."
docker compose build --no-cache
echo ""

# Inicia os serviços
echo "🚀 Iniciando serviços..."
docker compose up -d postgres app
echo ""

# Aguarda PostgreSQL ficar healthy
echo "⏳ Aguardando PostgreSQL ficar healthy..."
for i in {1..30}; do
    if docker inspect desafio2-postgres --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ PostgreSQL está healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""
echo ""

# Aguarda aplicação ficar healthy
echo "⏳ Aguardando aplicação ficar healthy..."
for i in {1..30}; do
    if docker inspect desafio2-app --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ Aplicação está healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""
echo ""

# Status dos containers
echo "📊 Status dos serviços:"
docker compose ps
echo ""

# Informações do volume
echo "💾 Volume persistente criado:"
docker volume inspect desafio2_postgres_data --format '{{.Name}}: {{.Mountpoint}}' 2>/dev/null
echo ""

echo "=========================================="
echo "✅ Ambiente iniciado com sucesso!"
echo "=========================================="
echo ""
echo "📝 Serviços disponíveis:"
echo "  - API REST:        http://localhost:5000"
echo "  - PostgreSQL:      localhost:5432"
echo ""
echo "📝 Comandos úteis:"
echo "  - Ver logs:               docker compose logs -f"
echo "  - Testar API:             ./scripts/test.sh"
echo "  - Adicionar dados:        ./scripts/populate.sh"
echo "  - Ler dados persistidos:  ./scripts/read_data.sh"
echo "  - Demonstrar persistência: ./scripts/demo_persistence.sh"
echo "  - Parar serviços:         docker compose down"
echo ""
