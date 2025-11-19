#!/bin/bash

# Script de demonstração completa

echo "=========================================="
echo "  DEMONSTRAÇÃO COMPLETA"
echo "  Microsserviços Independentes"
echo "=========================================="
echo ""

SERVICE_A="http://localhost:5000"
SERVICE_B="http://localhost:5001"

echo "🎯 Cenário: Sistema de gerenciamento de usuários e perfis"
echo ""
echo "Arquitetura:"
echo "  • Service A: Gerencia dados básicos de usuários"
echo "  • Service B: Consome Service A e enriquece com análises"
echo "  • Comunicação via HTTP (REST API)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Caso de uso 1: Listar usuários
echo "📋 Caso de Uso 1: Listar Usuários Ativos"
echo ""
echo "Service A retorna dados básicos:"
curl -s "$SERVICE_A/users?active=true" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total de usuários ativos: {data[\"total\"]}')
print()
print('Usuários:')
for user in data['users'][:3]:
    print(f'  • {user[\"full_name\"]} (@{user[\"username\"]}) - {user[\"role\"]}')
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Caso de uso 2: Perfil enriquecido
echo "👤 Caso de Uso 2: Perfil Enriquecido"
echo ""
echo "Comparando dados entre serviços para o usuário 'Alice'..."
echo ""

echo "📊 Service A (dados básicos):"
curl -s "$SERVICE_A/users/1" | python3 -c "
import sys, json
user = json.load(sys.stdin)['user']
print(f'  Nome: {user[\"full_name\"]}')
print(f'  Email: {user[\"email\"]}')
print(f'  Cargo: {user[\"role\"]}')
print(f'  Departamento: {user[\"department\"]}')
print(f'  Projetos: {len(user[\"projects\"])}')
print(f'  Skills: {len(user[\"skills\"])}')
"
echo ""

echo "✨ Service B (dados enriquecidos):"
curl -s "$SERVICE_B/profiles/1" | python3 -c "
import sys, json
profile = json.load(sys.stdin)['profile']
print(f'  Nome: {profile[\"full_name\"]}')
print(f'  Email: {profile[\"email\"]}')
print(f'  Cargo: {profile[\"professional\"][\"role\"]}')
print(f'  Departamento: {profile[\"professional\"][\"department\"]}')
print(f'  Nível de Experiência: {profile[\"professional\"][\"experience_level\"]} ⭐')
print(f'  Status de Atividade: {profile[\"activity\"][\"status\"]} 🟢')
print(f'  Tempo na empresa: {profile[\"metrics\"][\"tenure\"]} 📅')
print(f'  Projetos: {profile[\"metrics\"][\"total_projects\"]}')
print(f'  Skills: {profile[\"metrics\"][\"skill_count\"]}')
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Caso de uso 3: Resumo executivo
echo "📝 Caso de Uso 3: Resumo Executivo"
echo ""
echo "Service B gera descrição textual combinando dados:"
echo ""
curl -s "$SERVICE_B/profiles/2/summary" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'{data[\"summary\"]}')
print()
print('Destaques:')
for key, value in data['highlights'].items():
    print(f'  • {key.replace(\"_\", \" \").title()}: {value}')
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Caso de uso 4: Filtros
echo "🔍 Caso de Uso 4: Filtros por Departamento"
echo ""
echo "Service B aplica filtros consultando Service A:"
echo ""
curl -s "$SERVICE_B/profiles?department=Engineering" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Perfis no departamento Engineering: {data[\"total\"]}')
print()
for profile in data['profiles']:
    exp = profile['professional']['experience_level']
    status = profile['activity']['status']
    print(f'  • {profile[\"full_name\"]} - {profile[\"professional\"][\"role\"]} ({exp}, {status})')
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Caso de uso 5: Estatísticas
echo "📊 Caso de Uso 5: Estatísticas dos Serviços"
echo ""

echo "Service A (Users Service):"
curl -s "$SERVICE_A/stats" | python3 -c "
import sys, json
stats = json.load(sys.stdin)
print(f'  Total de requisições: {stats[\"requests\"][\"total\"]}')
print(f'  Total de usuários: {stats[\"users\"][\"total\"]}')
print(f'  Usuários ativos: {stats[\"users\"][\"active\"]}')
print(f'  Departamentos: {len(stats[\"users\"][\"by_department\"])}')
"
echo ""

echo "Service B (Profile Service):"
curl -s "$SERVICE_B/stats" | python3 -c "
import sys, json
stats = json.load(sys.stdin)
print(f'  Total de requisições: {stats[\"requests\"][\"total\"]}')
print(f'  Perfis gerados: {stats[\"requests\"][\"profiles_generated\"]}')
print(f'  Chamadas ao Service A: {stats[\"service_a_communication\"][\"total_calls\"]}')
print(f'  Taxa de erro: {stats[\"service_a_communication\"][\"error_rate_percent\"]}%')
"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "=========================================="
echo "✅ Demonstração Completa Concluída!"
echo "=========================================="
echo ""
echo "🎯 Conceitos demonstrados:"
echo "  ✓ Comunicação HTTP entre microsserviços"
echo "  ✓ Service A como fonte de dados"
echo "  ✓ Service B como consumidor e agregador"
echo "  ✓ Enriquecimento de dados"
echo "  ✓ Isolamento e independência dos serviços"
echo "  ✓ Health checks e monitoramento"
echo ""
