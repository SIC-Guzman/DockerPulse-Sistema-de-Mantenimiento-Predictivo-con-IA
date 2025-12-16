#!/bin/bash

echo "🔥 DOCKERPULSE – DEMO DE ESTRÉS (90s)"
echo "==================================="

# Contenedores
PRIMEROS=("oracle-db" "nginx-web" "redis-cache")
TODOS=("oracle-db" "nginx-web" "redis-cache" "postgres-db" "rabbitmq-msg" "python-api" "node-service")

echo ""
echo "🟢 FASE 1 (0–30s): Estresando 3 contenedores"
for c in "${PRIMEROS[@]}"; do
  echo "➡️  Estresando $c"
  docker exec -d "$c" stress-ng --cpu 1 --timeout 30s --quiet
done

sleep 30

echo ""
echo "🟡 FASE 2 (30–60s): Estresando 7 contenedores"
for c in "${TODOS[@]}"; do
  echo "➡️  Estresando $c"
  docker exec -d "$c" stress-ng --cpu 1 --timeout 30s --quiet
done

sleep 30

echo ""
echo "🔴 FASE 3 (60–90s): Estresando CPU del HOST"
CORES=$(nproc)
stress-ng --cpu "$CORES" --timeout 30s --quiet

echo ""
echo "✅ DEMO FINALIZADA"
