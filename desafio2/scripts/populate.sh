#!/bin/bash

# Script para popular o banco com dados de exemplo

echo "=========================================="
echo "  Populando Banco de Dados"
echo "=========================================="
echo ""

BASE_URL="http://localhost:5000"

# Cria tarefas de exemplo
echo "📝 Criando tarefas de exemplo..."
echo ""

# Tarefa 1
echo "1. Criando tarefa: Estudar Docker Volumes..."
curl -s -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Estudar Docker Volumes",
    "description": "Aprender sobre persistência de dados em containers",
    "status": "completed"
  }' | python3 -m json.tool
echo ""

# Tarefa 2
echo "2. Criando tarefa: Implementar API REST..."
curl -s -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implementar API REST",
    "description": "Criar endpoints CRUD para gerenciar tarefas",
    "status": "completed"
  }' | python3 -m json.tool
echo ""

# Tarefa 3
echo "3. Criando tarefa: Configurar PostgreSQL..."
curl -s -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Configurar PostgreSQL",
    "description": "Configurar banco de dados com volumes persistentes",
    "status": "completed"
  }' | python3 -m json.tool
echo ""

# Tarefa 4
echo "4. Criando tarefa: Testar persistência..."
curl -s -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Testar persistência de dados",
    "description": "Verificar se dados persistem após remover containers",
    "status": "in_progress"
  }' | python3 -m json.tool
echo ""

# Tarefa 5
echo "5. Criando tarefa: Documentar projeto..."
curl -s -X POST $BASE_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Documentar projeto",
    "description": "Criar README completo com explicações e prints",
    "status": "pending"
  }' | python3 -m json.tool
echo ""

echo ""
echo "=========================================="
echo "✅ Banco populado com sucesso!"
echo "=========================================="
echo ""

# Mostra estatísticas
echo "📊 Estatísticas atuais:"
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""
