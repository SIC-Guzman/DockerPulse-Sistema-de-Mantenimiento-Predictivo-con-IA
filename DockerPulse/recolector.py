import psutil
import docker
import time
import csv
import json
from datetime import datetime

client = docker.from_env()
nombre_archivo = 'datos_entrenamiento.csv'
archivo_tiempo_real = 'datos_en_vivo.json'

# LISTA DE TUS 7 CONTENEDORES
NODOS = [
    ('oracle-db', 'ORA'), 
    ('nginx-web', 'WEB'), 
    ('redis-cache', 'RED'), 
    ('postgres-db', 'POS'), 
    ('rabbitmq-msg', 'RAB'), 
    ('python-api', 'PYT'), 
    ('node-service', 'NOD')
]

# Preparamos encabezados del CSV
encabezados = ['Timestamp', 'Host_CPU', 'Host_RAM']
for nombre_real, nombre_corto in NODOS:
    encabezados.append(f"{nombre_real}_CPU")
    encabezados.append(f"{nombre_real}_RAM")

# Abrir CSV en modo escritura
with open(nombre_archivo, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(encabezados)

print(f"🚀 DOCKERPULSE MONITOR TOTAL... Guardando en {nombre_archivo}")

try:
    while True:
        # 1. DATOS DEL HOST
        host_cpu = psutil.cpu_percent()
        host_ram = psutil.virtual_memory().percent
        
        fila_datos = [datetime.now().strftime("%H:%M:%S"), host_cpu, host_ram]
        
        datos_json = {
            "timestamp": fila_datos[0],
            "host": {"cpu": host_cpu, "ram": host_ram},
            "contenedores": []
        }

        mensaje_pantalla = f"PC:{str(round(host_cpu,1)).rjust(4)}% | "

        # 2. BUCLE CONTENEDORES
        for nombre_real, nombre_corto in NODOS:
            cpu = 0.0
            ram = 0.0
            try:
                cont = client.containers.get(nombre_real)
                stats = cont.stats(stream=False)
                
                # CPU
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                sys_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                if sys_delta > 0.0:
                    cpu = (cpu_delta / sys_delta) * 100.0 * psutil.cpu_count()
                
                # RAM
                ram = (stats['memory_stats']['usage'] / stats['memory_stats']['limit']) * 100
            except:
                pass 

            # Agregar datos
            fila_datos.append(round(cpu, 2))
            fila_datos.append(round(ram, 2))
            
            datos_json["contenedores"].append({
                "nombre": nombre_real,
                "cpu": round(cpu, 2),
                "ram": round(ram, 2)
            })

            mensaje_pantalla += f"{nombre_corto}:{str(round(cpu,1)).rjust(4)}% | "

        # 3. GUARDAR
        with open(nombre_archivo, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(fila_datos)

        with open(archivo_tiempo_real, 'w') as json_file:
            json.dump(datos_json, json_file)

        print(mensaje_pantalla)
        time.sleep(1)

except KeyboardInterrupt:
    print("\n✅ Monitoreo detenido.")
