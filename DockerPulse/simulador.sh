#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' 


ALL_7="oracle-db nginx-web redis-cache postgres-db rabbitmq-msg python-api node-service"
TOP_5="oracle-db nginx-web redis-cache postgres-db rabbitmq-msg"
TOP_3="oracle-db nginx-web redis-cache"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${RED}    💀 DOCKERPULSE: SIMULADOR DE CAOS    ${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo "Selecciona el nivel de destrucción (Duran 60 segs):"
echo ""
echo -e "1) ${GREEN}Nivel Básico:${NC} Estresar Top 3 (Oracle, Web, Redis)"
echo -e "2) ${YELLOW}Nivel Medio:${NC}  Estresar Top 5 (Incluye Postgres y Rabbit)"
echo -e "3) ${RED}Nivel Alto:${NC}   Estresar TODOS los 7 Contenedores"
echo -e "4) ${RED}🔥 NIVEL DIOS:${NC}  TODOS los Contenedores + TU PC (Host)"
echo ""
echo -n "Elige una opción (1-4): "
read opcion


atacar_docker() {
    lista=$1
    echo -e "\n${RED}🚀 Lanzando carga al 100% en: $lista ${NC}"
    for contenedor in $lista; do
        
        docker exec -d $contenedor sh -c "timeout 60s sh -c 'while true; do :; done'"
    done
}

case $opcion in
    1)
        atacar_docker "$TOP_3"
        ;;
    2)
        atacar_docker "$TOP_5"
        ;;
    3)
        atacar_docker "$ALL_7"
        ;;
    4)
        atacar_docker "$ALL_7"
        echo -e "${RED}💻 Estresando CPU del HOST (Tu PC)...${NC}"
        # Estresa 4 núcleos de tu PC por 60 segundos
        stress-ng --cpu 4 --timeout 60s &
        ;;
    *)
        echo "Opción no válida."
        exit 1
        ;;
esac

echo -e "\n${YELLOW}⏳ Ataque en curso... Durará 60 segundos.${NC}"
echo "Mira la otra terminal para ver cómo suben los gráficos."
echo "El ataque se detendrá solo automáticamente."
