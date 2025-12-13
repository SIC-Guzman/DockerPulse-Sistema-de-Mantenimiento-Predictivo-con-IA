# DockerPulse: Sistema de Mantenimiento Predictivo con Inteligencia Artificial

## Descripción del Proyecto

DockerPulse es una solución integral de monitoreo inteligente diseñada para infraestructuras críticas basadas en contenedores Docker. A diferencia de los monitores tradicionales que solo alertan cuando algo ya se rompió, DockerPulse utiliza Inteligencia Artificial para predecir fallos antes de que ocurran, detectar anomalías y visualizar el estado de los servicios en tiempo real mediante un dashboard interactivo.

El sistema despliega una arquitectura de microservicios empresarial y aplica técnicas de Chaos Engineering para entrenar modelos predictivos capaces de detectar:

- Saturación de CPU/RAM en tiempo real
- Anomalías de seguridad y comportamiento
- Patrones de caída inminente en bases de datos y servidores web
- Tendencias predictivas de uso de recursos

### Objetivo Principal

Reducir el tiempo de inactividad (Downtime) en servidores empresariales mediante la predicción temprana de incidentes, anticipándose a problemas críticos antes de que provoquen caídas del sistema y mejorando la toma de decisiones del equipo de operaciones.

## Propuesta de Valor

La mayoría de herramientas de monitoreo tradicionales son reactivas: alertan cuando el problema ya ocurrió. DockerPulse cambia este enfoque incorporando:

- Monitoreo en tiempo real de métricas críticas
- Predicción con IA supervisada utilizando redes neuronales
- Detección de anomalías con algoritmos no supervisados
- Dashboard visual e intuitivo para operaciones
- Arquitectura escalable y modular

## Arquitectura del Sistema

El sistema simula un entorno corporativo real orquestando 7 Contenedores Docker críticos y está dividido en cuatro componentes principales:

### Infraestructura de Contenedores

| Servicio | Tecnología | Función |
|:---------|:-----------|:--------|
| Base de Datos Principal | Oracle Database | Gestión de datos transaccionales |
| Servidor Web | Nginx | Balanceador de carga y entrada web |
| Caché | Redis | Almacenamiento rápido en memoria |
| Finanzas | PostgreSQL | Base de datos relacional secundaria |
| Mensajería | RabbitMQ | Cola de mensajes entre servicios |
| Backend API | Python (Flask) | Lógica de negocio |
| Microservicio | Node.js | Servicio auxiliar ligero |

### Componentes del Sistema

**1. Recolector de Métricas**
- Extrae métricas del host y contenedores Docker en tiempo real
- Genera el archivo `datos_en_vivo.json` para el pipeline de datos
- Utiliza Docker SDK y psutil para telemetría precisa

**2. Preprocesamiento de Datos**
- Limpieza y normalización de datos
- Selección de características relevantes
- Escalado y transformación para compatibilidad con modelos

**3. Módulo de Inteligencia Artificial**
- Modelo supervisado (TensorFlow/Keras): predice la CPU futura del host
- Modelo no supervisado (K-Means): detecta anomalías en comportamiento
- Pipeline de entrenamiento continuo

**4. Backend y Frontend**
- Backend en FastAPI expone una API REST robusta
- Frontend en Vue 3 muestra dashboard en tiempo real
- Actualización automática cada 2 segundos

## Tecnologías Utilizadas

### Backend e Inteligencia Artificial
- Python 3.9+
- FastAPI
- TensorFlow / Keras
- Scikit-learn
- Pandas / NumPy
- Docker SDK
- psutil

### Frontend
- Vue 3
- Vite
- JavaScript ES6+
- CSS moderno (dashboard oscuro industrial)

### Infraestructura
- Docker
- Docker Compose
- Linux (Pop!_OS / Ubuntu recomendado) o Windows con WSL2

## Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado:

- Linux (Recomendado: Pop!_OS / Ubuntu) o Windows con WSL2
- Docker y Docker Compose
- Python 3.9 o superior
- Node.js y npm (Para el Frontend)
- Git

## Estructura del Proyecto

```
DockerPulse-Sistema-de-Mantenimiento-Predictivo-con-IA/
│
├── DockerPulse/
│   ├── recolector.py
│   ├── simulador.sh
│   ├── demo_express.sh
│   └── datos_en_vivo.json
│
├── src/
│   ├── servicio_ia.py
│   ├── preprocesamiento.py
│   ├── entrenamiento_prediccion.py
│   └── entrenamiento_anomalias.py
│
├── models/
│   ├── modelo_prediccion.h5
│   ├── modelo_anomalia.pkl
│   └── scaler_features.pkl
│
├── frontend/
│   ├── src/
│   │   └── App.vue
│   └── package.json
│
├── docker-compose.yml
├── requirements.txt
├── datos_entrenamiento.csv
└── README.md
```

## Guía de Instalación y Ejecución

El proyecto requiere tres terminales diferentes ejecutándose simultáneamente.

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/DockerPulse.git
cd DockerPulse
```

### Paso 2: Levantar la Infraestructura Docker

Iniciar los 7 contenedores que simulan el entorno empresarial:

```bash
docker start oracle-db nginx-web redis-cache postgres-db rabbitmq-msg python-api node-service

docker ps
```

### Paso 3: Levantar el Backend (Terminal 1)

```bash
cd "/ruta/al/proyecto/DockerPulse-Sistema-de-Mantenimiento-Predictivo-con-IA"

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python3 -m uvicorn src.servicio_ia:app --reload --host 0.0.0.0 --port 8000
```

Verificación: Abrir navegador en http://localhost:8000/api/status para confirmar que el backend responde correctamente.

### Paso 4: Ejecutar el Recolector de Métricas (Terminal 2)

```bash
sudo systemctl start docker

cd "/ruta/al/proyecto/DockerPulse-Sistema-de-Mantenimiento-Predictivo-con-IA/DockerPulse"

python3 recolector.py
```

Verificación: La consola mostrará métricas en tiempo real y se generará/actualizará el archivo `datos_en_vivo.json`.

### Paso 5: Levantar el Frontend (Terminal 3)

```bash
cd "/ruta/al/proyecto/DockerPulse-Sistema-de-Mantenimiento-Predictivo-con-IA/frontend"

npm install

npm run dev
```

Verificación: Abrir navegador en http://localhost:5173 para visualizar el dashboard en tiempo real.

## Modo Chaos Engineering (Simulador de Fallos)

Para demostrar la capacidad predictiva de la IA, el sistema incluye herramientas para simular fallos controlados.

### Opción A: Ataque Manual

```bash
./simulador.sh
```

Permite seleccionar entre 4 niveles de intensidad de carga.

### Opción B: Demo Express (Presentación de 90 segundos)

```bash
./demo_express.sh
```

Ejecuta una secuencia automática: Carga Media → Carga Alta → Colapso Total, ideal para demostraciones.

## Funcionalidades Principales

- **Semáforo Global de Estado:** Indicador visual del estado general del sistema (Normal, Advertencia, Crítico)
- **Predicción de CPU Futura:** Modelo de TensorFlow predice el uso de CPU del host
- **Detección de Anomalías:** Algoritmo K-Means identifica comportamientos atípicos
- **Monitoreo Individual por Contenedor:** Métricas detalladas de CPU, RAM y estado
- **Interpretación Visual Clara:** Dashboard diseñado para toma rápida de decisiones
- **Actualización en Tiempo Real:** Refresco automático cada 2 segundos

## Casos de Uso

- Equipos DevOps y SRE (Site Reliability Engineering)
- Infraestructura crítica empresarial
- Sistemas basados en microservicios
- Ambientes de pruebas y producción
- Proyectos académicos de Inteligencia Artificial

## Conclusión

DockerPulse representa una evolución significativa en el monitoreo de infraestructuras modernas, demostrando cómo la Inteligencia Artificial puede transformar sistemas reactivos en plataformas predictivas capaces de anticiparse a fallos críticos. La combinación de técnicas de aprendizaje supervisado y no supervisado, junto con una arquitectura escalable basada en microservicios, posiciona a DockerPulse como una solución robusta para entornos empresariales que requieren alta disponibilidad y gestión proactiva de incidentes.