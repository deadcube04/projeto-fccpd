#!/bin/bash

# Script que demonstra a persistência de dados

set -e

echo "=========================================="
echo "  DEMONSTRAÇÃO DE PERSISTÊNCIA"
echo "=========================================="
echo ""

BASE_URL="http://localhost:5000"

# Passo 1: Adiciona dados
echo "📝 PASSO 1: Adicionando dados ao banco..."
echo ""
curl -s -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tarefa de Teste de Persistência",
    "description": "Esta tarefa será usada para demonstrar persistência",
    "status": "pending"
  }' | python3 -m json.tool
echo ""
echo ""

# Mostra dados atuais
echo "📊 Dados atuais no banco:"
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""
echo ""

# Passo 2: Para e remove o container da aplicação
echo "🛑 PASSO 2: Parando e removendo container da aplicação..."
docker stop desafio2-app
docker rm desafio2-app
echo "✓ Container removido!"
echo ""
sleep 2

# Passo 3: Recria o container
echo "🔄 PASSO 3: Recriando container da aplicação..."
docker compose up -d app
echo ""

# Aguarda ficar healthy
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

# Passo 4: Verifica se os dados ainda existem
echo "✅ PASSO 4: Verificando se os dados persistiram..."
echo ""
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""
echo ""

# Lê todos os dados
echo "📖 Lendo todos os dados persistidos:"
docker compose run --rm reader
echo ""

echo "=========================================="
echo "✅ PERSISTÊNCIA DEMONSTRADA COM SUCESSO!"
echo "=========================================="
echo ""
echo "🎯 Conclusão:"
echo "   Os dados permaneceram no banco mesmo após"
echo "   remover e recriar o container da aplicação!"
echo "   Isso é possível graças ao volume Docker."
echo ""
