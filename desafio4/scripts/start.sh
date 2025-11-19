#!/bin/bash

# Script para iniciar o Desafio 4 - Microsserviços Independentes

set -e

echo "=========================================="
echo "  Desafio 4 - Microsserviços"
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

# Limpa containers antigos
echo "🧹 Limpando containers antigos..."
docker compose down 2>/dev/null || true
echo ""

# Constrói as imagens
echo "🔨 Construindo imagens Docker..."
docker compose build --no-cache
echo ""

# Inicia os serviços
echo "🚀 Iniciando serviços..."
docker compose up -d
echo ""

# Aguarda Service A ficar healthy
echo "⏳ Aguardando Service A (Users Service)..."
for i in {1..30}; do
    if docker inspect desafio4-service-a --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ Service A está healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Aguarda Service B ficar healthy
echo "⏳ Aguardando Service B (Profile Service)..."
for i in {1..30}; do
    if docker inspect desafio4-service-b --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ Service B está healthy!"
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
docker network inspect desafio4-network --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}' 2>/dev/null
echo ""

echo "=========================================="
echo "✅ Ambiente iniciado com sucesso!"
echo "=========================================="
echo ""
echo "📝 Serviços disponíveis:"
echo "  - Service A (Users):    http://localhost:5000"
echo "  - Service B (Profiles): http://localhost:5001"
echo ""
echo "📝 Comandos úteis:"
echo "  - Ver logs:                    docker compose logs -f"
echo "  - Testar comunicação:          ./scripts/test_communication.sh"
echo "  - Testar endpoints:            ./scripts/test.sh"
echo "  - Demonstração completa:       ./scripts/demo.sh"
echo "  - Ver estatísticas:            ./scripts/stats.sh"
echo "  - Parar serviços:              docker compose down"
echo ""
