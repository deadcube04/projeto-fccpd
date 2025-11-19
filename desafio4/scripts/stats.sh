#!/bin/bash

# Script para exibir estatísticas

echo "=========================================="
echo "  Estatísticas dos Microsserviços"
echo "=========================================="
echo ""

SERVICE_A="http://localhost:5000"
SERVICE_B="http://localhost:5001"

echo "📊 SERVICE A - USERS SERVICE"
echo ""
curl -s $SERVICE_A/stats | python3 -m json.tool
echo ""
echo ""

echo "📊 SERVICE B - PROFILE SERVICE"
echo ""
curl -s $SERVICE_B/stats | python3 -m json.tool
echo ""
