#!/bin/bash

echo "🤖 INICIANDO MODO AUTOMÁTICO - DURACIÓN: 60 MINUTOS"
echo "Relájate, yo me encargo de estresar el sistema..."

# Función para contar tiempo
esperar() {
    segundos=$1
    echo "   ... Esperando $segundos segundos (Recuperación)..."
    sleep $segundos
}

# Bucle que se repetirá 10 veces (aprox 60 mins total)
for i in {1..10}
do
    echo "=========================================="
    echo "🔄 CICLO $i DE 10"
    echo "=========================================="

    # 1. CALMA (2 Minutos) - Para que la IA vea datos normales
    echo "🟢 [FASE 1] Tráfico Normal (2 min)"
    esperar 120

    # 2. ATAQUE NIVEL 1 - Top 3 (1 Minuto)
    echo "🟡 [FASE 2] Ataque Básico: Oracle, Web, Redis"
    ./simulador.sh << EOF
1
EOF
    # (El simulador tarda 60s en ejecutarse)
    esperar 10 # Pequeño respiro

    # 3. CALMA CORTA (1 Minuto)
    echo "🟢 [FASE 3] Recuperación breve (1 min)"
    esperar 60

    # 4. ATAQUE NIVEL 2 - Top 5 (1 Minuto)
    echo "🟠 [FASE 4] Carga Media: Bases de Datos + Mensajería"
    ./simulador.sh << EOF
2
EOF
    esperar 10

    # 5. ATAQUE NIVEL DIOS (Solo en ciclos pares para no quemar la PC)
    if (( $i % 2 == 0 )); then
        echo "🔥 [FASE 5] ¡APOCALIPSIS! (Host + Todos los Contenedores)"
        ./simulador.sh << EOF
4
EOF
    else
        echo "🔴 [FASE 5] Carga Alta (Solo Contenedores)"
        ./simulador.sh << EOF
3
EOF
    fi
    
    echo "✅ Fin del ciclo $i."
done

echo "🎉 ENTRENAMIENTO DE 1 HORA COMPLETADO."
