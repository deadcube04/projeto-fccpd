#!/bin/bash

# Script para iniciar o Desafio 5 - API Gateway

set -e

echo "=========================================="
echo "  Desafio 5 - API Gateway"
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

# Aguarda Users Service ficar healthy
echo "⏳ Aguardando Users Service..."
for i in {1..30}; do
    if docker inspect desafio5-users --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ Users Service está healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Aguarda Orders Service ficar healthy
echo "⏳ Aguardando Orders Service..."
for i in {1..30}; do
    if docker inspect desafio5-orders --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ Orders Service está healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Aguarda Gateway ficar healthy
echo "⏳ Aguardando API Gateway..."
for i in {1..30}; do
    if docker inspect desafio5-gateway --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✓ API Gateway está healthy!"
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
docker network inspect desafio5-network --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}' 2>/dev/null
echo ""

echo "=========================================="
echo "✅ Ambiente iniciado com sucesso!"
echo "=========================================="
echo ""
echo "📝 Acesso aos serviços:"
echo "  - API Gateway (ponto único):  http://localhost:8000"
echo "  - Users Service (direto):     http://localhost:5001 (não exposto)"
echo "  - Orders Service (direto):    http://localhost:5002 (não exposto)"
echo ""
echo "💡 IMPORTANTE: Todos os acessos devem ser feitos via Gateway!"
echo ""
echo "📝 Comandos úteis:"
echo "  - Ver logs:                    docker compose logs -f"
echo "  - Testar gateway:              ./scripts/test.sh"
echo "  - Demonstração completa:       ./scripts/demo.sh"
echo "  - Testar orquestração:         ./scripts/test_orchestration.sh"
echo "  - Ver estatísticas:            curl http://localhost:8000/stats"
echo "  - Parar serviços:              docker compose down"
echo ""
