#!/bin/bash
# demo_express.sh - 90 segundos de caos controlado

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TOP_3="oracle-db nginx-web redis-cache"
ALL_7="oracle-db nginx-web redis-cache postgres-db rabbitmq-msg python-api node-service"

echo -e "${RED}🚀 INICIANDO DEMO DOCKERPULSE (90 SEGUNDOS) 🚀${NC}"
echo "3..."
sleep 1
echo "2..."
sleep 1
echo "1..."
sleep 1

# FASE 1: 30s Carga Media
echo -e "\n${GREEN}[00-30s] FASE 1: Estrés Medio (Top 3 Servicios)${NC}"
for cont in $TOP_3; do
    docker exec -d $cont sh -c "timeout 30s sh -c 'while true; do :; done'"
done
# Espera visual
echo -n "Cargando..."
for i in {1..30}; do echo -n "▓"; sleep 1; done
echo ""

# FASE 2: 30s Carga Alta
echo -e "\n${YELLOW}[30-60s] FASE 2: Estrés Alto (Todos los servicios)${NC}"
for cont in $ALL_7; do
    docker exec -d $cont sh -c "timeout 30s sh -c 'while true; do :; done'"
done
echo -n "Saturando..."
for i in {1..30}; do echo -n "▓"; sleep 1; done
echo ""

# FASE 3: 30s Nivel Dios
echo -e "\n${RED}[60-90s] FASE 3: COLAPSO TOTAL (Host + Docker)${NC}"
for cont in $ALL_7; do
    docker exec -d $cont sh -c "timeout 30s sh -c 'while true; do :; done'"
done
stress-ng --cpu 4 --timeout 30s &
echo -n "🔥 FUEGO 🔥..."
for i in {1..30}; do echo -n "▓"; sleep 1; done
echo ""

echo -e "\n${BLUE}✅ DEMO TERMINADA.${NC}"
