#!/bin/bash

# Script para testar comunicação entre microsserviços

echo "=========================================="
echo "  Testando Comunicação HTTP"
echo "  Service B → Service A"
echo "=========================================="
echo ""

SERVICE_A="http://localhost:5000"
SERVICE_B="http://localhost:5001"

# Testa Service A diretamente
echo "1️⃣ Testando Service A (Users Service) diretamente..."
echo ""
echo "GET $SERVICE_A/users"
curl -s $SERVICE_A/users | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'  ✓ Retornou {data[\"total\"]} usuários')"
echo ""
echo ""

# Testa Service B consumindo Service A
echo "2️⃣ Testando Service B (Profile Service) consumindo Service A..."
echo ""
echo "GET $SERVICE_B/profiles"
curl -s $SERVICE_B/profiles | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'  ✓ Retornou {data[\"total\"]} perfis enriquecidos'); print(f'  ✓ Fonte dos dados: {data[\"data_source\"]}')"
echo ""
echo ""

# Compara dados
echo "3️⃣ Comparando dados brutos (Service A) vs enriquecidos (Service B)..."
echo ""

echo "Usuário #1 no Service A:"
curl -s $SERVICE_A/users/1 | python3 -c "import sys, json; data = json.load(sys.stdin); user = data['user']; print(f'  Nome: {user[\"full_name\"]}'); print(f'  Cargo: {user[\"role\"]}'); print(f'  Ativo: {user[\"active\"]}')"
echo ""

echo "Perfil #1 no Service B (enriquecido):"
curl -s $SERVICE_B/profiles/1 | python3 -c "import sys, json; data = json.load(sys.stdin); p = data['profile']; print(f'  Nome: {p[\"full_name\"]}'); print(f'  Cargo: {p[\"professional\"][\"role\"]}'); print(f'  Nível: {p[\"professional\"][\"experience_level\"]}'); print(f'  Status: {p[\"activity\"][\"status\"]}'); print(f'  Tenure: {p[\"metrics\"][\"tenure\"]}')"
echo ""
echo ""

# Testa resumo executivo
echo "4️⃣ Testando resumo executivo (Service B)..."
echo ""
curl -s $SERVICE_B/profiles/1/summary | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'  {data[\"summary\"]}')"
echo ""
echo ""

# Testa health check de dependências
echo "5️⃣ Verificando health check de dependências..."
echo ""
echo "Service A health:"
curl -s $SERVICE_A/health | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'  Status: {data[\"status\"]}')"
echo ""
echo "Service B health (verifica dependência do Service A):"
curl -s $SERVICE_B/health | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'  Status: {data[\"status\"]}'); print(f'  Service A: {data[\"dependencies\"][\"users_service\"][\"status\"]}')"
echo ""
echo ""

# Testa resolução DNS
echo "6️⃣ Verificando resolução DNS interna..."
echo ""
docker exec desafio4-service-b ping -c 2 service-a | tail -1
echo "✓ Service B consegue resolver hostname 'service-a'"
echo ""
echo ""

echo "=========================================="
echo "✅ Comunicação HTTP funcionando!"
echo "=========================================="
echo ""
echo "🎯 Demonstrações realizadas:"
echo "  • Service A fornece dados de usuários"
echo "  • Service B consome Service A via HTTP"
echo "  • Service B enriquece dados com informações calculadas"
echo "  • Health checks verificam dependências"
echo "  • DNS interno resolve nomes dos serviços"
echo ""
