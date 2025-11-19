#!/bin/bash

# Script para popular o banco com produtos de exemplo

echo "=========================================="
echo "  Populando Catálogo de Produtos"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

# Cria produtos de exemplo
echo "📦 Criando produtos de exemplo..."
echo ""

# Eletrônicos
echo "1. Smartphone Premium..."
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smartphone Premium XZ",
    "description": "Smartphone de última geração com 256GB",
    "price": 2999.99,
    "stock": 50,
    "category": "electronics"
  }' | python3 -m json.tool
echo ""

echo "2. Notebook Gamer..."
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Notebook Gamer Pro",
    "description": "Notebook com RTX 4060, 16GB RAM, SSD 512GB",
    "price": 5499.00,
    "stock": 25,
    "category": "electronics"
  }' | python3 -m json.tool
echo ""

echo "3. Fone Bluetooth..."
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fone Bluetooth Premium",
    "description": "Fone com cancelamento de ruído ativo",
    "price": 799.90,
    "stock": 100,
    "category": "electronics"
  }' | python3 -m json.tool
echo ""

# Livros
echo "4. Livro - Clean Code..."
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clean Code - Robert Martin",
    "description": "Guia essencial para escrever código limpo",
    "price": 89.90,
    "stock": 150,
    "category": "books"
  }' | python3 -m json.tool
echo ""

echo "5. Livro - Design Patterns..."
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Design Patterns - Gang of Four",
    "description": "Padrões de projeto essenciais",
    "price": 95.00,
    "stock": 80,
    "category": "books"
  }' | python3 -m json.tool
echo ""

# Esportes
echo "6. Tênis Running..."
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tênis Running Pro",
    "description": "Tênis para corrida com amortecimento avançado",
    "price": 459.90,
    "stock": 60,
    "category": "sports"
  }' | python3 -m json.tool
echo ""

echo "7. Bicicleta Mountain Bike..."
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mountain Bike 29",
    "description": "Bicicleta 21 marchas com suspensão",
    "price": 1899.00,
    "stock": 15,
    "category": "sports"
  }' | python3 -m json.tool
echo ""

# Casa
echo "8. Cafeteira Elétrica..."
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cafeteira Elétrica Premium",
    "description": "Cafeteira programável com timer",
    "price": 299.00,
    "stock": 40,
    "category": "home"
  }' | python3 -m json.tool
echo ""

echo ""
echo "=========================================="
echo "✅ Catálogo populado com sucesso!"
echo "=========================================="
echo ""

# Mostra estatísticas
echo "📊 Estatísticas atuais:"
curl -s $BASE_URL/stats | python3 -m json.tool
echo ""
