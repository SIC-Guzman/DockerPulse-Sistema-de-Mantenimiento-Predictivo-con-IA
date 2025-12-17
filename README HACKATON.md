# DockerPulse: AI-Driven Infrastructure Sentinel

## Resumen Ejecutivo

DockerPulse no es simplemente un monitor de recursos; es una Plataforma de Operaciones Inteligentes (AIOps) diseñada para la autogestión de infraestructuras críticas. Utilizando algoritmos de aprendizaje automático supervisado y heurísticas de detección de anomalías, el sistema transforma la telemetría bruta de los contenedores Docker en decisiones ejecutables en tiempo real.

El sistema cierra la brecha entre la Detección de Incidentes y la Resolución de Incidentes, automatizando la generación de reportes forenses y simulando protocolos de autosanación (Self-Healing) antes de que un fallo catastrófico afecte la disponibilidad del servicio.

---

## El Problema vs. La Solución

### El Desafío: La Fatiga de Alertas

En los sistemas tradicionales (Zabbix, Nagios, Prometheus), los ingenieros reciben miles de alertas cuando el servidor ya ha fallado. Esto resulta en:

- Tiempos de inactividad (Downtime) costosos
- Diagnósticos tardíos
- Pérdida de logs críticos durante el colapso

### La Solución DockerPulse

Nuestra arquitectura propone un cambio de paradigma: Del Monitoreo Reactivo a la Auditoría Predictiva.

1. **Predicción:** Anticipamos la saturación de CPU mediante análisis de series temporales
2. **Intervención:** Un motor de reglas lógico decide si el contenedor necesita reinicio o aislamiento
3. **Auditoría:** Generación instantánea de documentación legal/técnica (HTML) sobre el incidente para cumplimiento normativo

---

## Arquitectura Técnica del Sistema

El ecosistema DockerPulse se basa en una arquitectura de microservicios desacoplada, garantizando que el sistema de monitoreo no consuma los recursos que está vigilando.

### 1. Capa de Infraestructura (The Target)

Simulamos un entorno de producción real con 7 servicios orquestados:

| Servicio | Tecnología | Función |
|----------|------------|---------|
| Base de Datos Principal | Oracle Database | Gestión de datos transaccionales |
| Servidor Web | Nginx | Balanceador de carga y entrada web |
| Caché | Redis | Almacenamiento rápido en memoria |
| Finanzas | PostgreSQL | Base de datos relacional secundaria |
| Mensajería | RabbitMQ | Cola de mensajes entre servicios |
| Backend API | Python (Flask) | Lógica de negocio |
| Microservicio | Node.js | Servicio auxiliar ligero |

### 2. El Núcleo de Inteligencia (The Brain)

- **Framework:** FastAPI (Python) para procesamiento asíncrono de alta velocidad
- **Ingesta de Datos:** Recolección de métricas vía Docker SDK y psutil con latencia menor a 50ms
- **Motor de Inferencia:**
  - Modelo Predictivo: Regresión lineal ajustada dinámicamente para prever tendencias de uso de CPU a t+10 segundos
  - Detección de Anomalías: Análisis de desviación estándar (Z-Score) para identificar comportamientos fuera del perfil base del contenedor

### 3. Interfaz de Comando y Control (The UI)

- **Tecnología:** Streamlit (Python puro)
- **Justificación:** Se eliminó la sobrecarga de frameworks JS (React/Vue) para priorizar la velocidad de renderizado de datos científicos y la estabilidad en entornos de "War Room"
- **Features:** Renderizado de métricas en vivo, gestión de estado de sesión persistente y generación de documentos al vuelo

---

## Características Principales

### Módulo de Predicción de Riesgo

No solo le decimos cuánto CPU se usa ahora, le decimos cuánto se usará en el futuro inmediato.

- **Input:** Ventana deslizante de los últimos 60 segundos de telemetría
- **Output:** Probabilidad de fallo del sistema (0-100%)
- **Visualización:** Semáforo de Riesgo (Bajo/Medio/Crítico)

### Generador de Auditoría Forense (HTML Engine)

En caso de incidente, los equipos de DevOps odian escribir reportes manuales. DockerPulse lo hace por ellos.

- **Formato:** HTML Estilizado (Corporate Standard)
- **Contenido:**
  - ID Único de Incidente (UUID v4)
  - Timestamp exacto (ms)
  - Snapshot de métricas al momento del fallo
  - Historial de intervenciones previas de la IA
  - Sello de "Reinicio Forzado"

### Mecanismo de Autosanación Simulado

El sistema mantiene un Registro de Persistencia en Memoria.

- Rastrea cuántas veces un contenedor ha entrado en zona crítica
- Simula la ejecución de comandos docker restart cuando el umbral de confianza de la IA supera el 85%
- Muestra un contador de "Intervenciones Automáticas" en el dashboard

---

## Requisitos del Sistema

Para garantizar el rendimiento del modelo predictivo:

| Componente | Requisito Mínimo | Recomendado |
|------------|------------------|-------------|
| OS | Linux (Ubuntu 20.04+) / WSL2 | Pop!_OS / Debian 11 |
| Python | Versión 3.9 | Versión 3.10+ |
| Docker | Engine 20.10+ | Engine 24.0+ |
| RAM | 4 GB | 8 GB+ (Para simulación de carga) |
| Cores | 2 vCPU | 4 vCPU |

---

## Guía de Instalación y Despliegue

Sigue este procedimiento para desplegar la suite completa. Se recomienda el uso de 3 terminales separadas para visualizar todos los componentes.

### Paso 0: Preparación del Entorno

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/DockerPulse-AI.git
cd DockerPulse-AI

# Crear entorno virtual aislado (Best Practice)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias del núcleo
pip install -r requirements.txt
```

### Paso 1: Orquestación de Infraestructura (Terminal A)

Levantamos los 7 microservicios objetivo y la API de Inteligencia Artificial.

```bash
# Iniciar contenedores en segundo plano
docker-compose up -d

# Iniciar el Backend (Cerebro IA)
# El flag --reload permite cambios en caliente
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Nota: Esperar hasta ver el mensaje: "Application startup complete".

### Paso 2: Centro de Comando Visual (Terminal B)

Lanzamos el Dashboard de Ingeniería construido con Streamlit.

```bash
source venv/bin/activate
streamlit run src/dashboard.py
```

Nota: Esto abrirá automáticamente su navegador predeterminado en http://localhost:8501

### Paso 3: Inyección de Caos (Terminal C)

Para la demostración ante jurado, utilizaremos el script de estrés stress_demo.sh que simula un ataque DDoS o una fuga de memoria.

```bash
chmod +x scripts/stress_demo.sh
./scripts/stress_demo.sh
```

Advertencia: Este script elevará el uso de CPU de su máquina real para forzar la reacción de la IA.

---

## Escenario de Demostración (Demo Flow)

1. **Estado Basal:** El sistema muestra métricas verdes. El riesgo es "BAJO". La predicción es estable.
2. **Inyección de Fallo:** Se ejecuta el script de estrés. La CPU sube al 80-90%.
3. **Reacción de la IA:**
   - El indicador "PREDICCIÓN" se dispara antes que la métrica real
   - El "RIESGO IA" cambia a ALTO
   - El contador de "Intervenciones automáticas" en las tarjetas de contenedores comienza a subir
4. **Evidencia:** El usuario hace clic en "Descargar Auditoría". Se descarga un reporte HTML profesional que certifica el incidente y la acción correctiva tomada.

---

## Estructura del Proyecto

```
DockerPulse-AI/
│
├── src/
│   ├── main.py                # Cerebro (FastAPI Backend)
│   ├── dashboard.py           # Rostro (Streamlit UI + Reportes)
│   └── logic/                 # Lógica de ML y Docker
│
├── scripts/
│   ├── stress_demo.sh         # El "Virus" (Generador de carga)
│   └── setup_containers.sh    # Despliegue de infraestructura
│
├── generated_reports/         # Carpeta de salida para reportes HTML
├── requirements.txt           # Dependencias Python
├── docker-compose.yml         # Orquestación
└── README.md
```

---

## Tecnologías Utilizadas

### Stack Backend e IA

- Python 3.9+
- FastAPI - API asíncrona de alto rendimiento
- Streamlit - Dashboard de ingeniería con renderizado científico
- Pandas / NumPy - Procesamiento y análisis de datos
- Scikit-learn - Modelos predictivos y detección de anomalías
- Docker SDK - Control programático de contenedores

### Infraestructura

- Docker & Docker Compose - Orquestación de microservicios
- Linux (Ubuntu / Pop!_OS) o WSL2 para Windows

---

## Casos de Uso

- **Auditoría de Sistemas:** Generación de evidencia forense post-incidente
- **NOC (Network Operations Center):** Pantalla principal para vigilancia de servidores
- **Sistemas Autónomos:** Mantenimiento de servidores sin intervención humana
- **Equipos DevOps y SRE:** Transición de operaciones reactivas a predictivas
- **Cumplimiento Normativo:** Documentación automática para auditorías

---

## Roadmap y Futuro del Proyecto

- **Q1 2025:** Integración con Kubernetes (K8s) para gestión de Pods
- **Q2 2025:** Notificaciones proactivas vía Slack/Teams Webhooks
- **Q3 2025:** Módulo de análisis de logs con NLP (Procesamiento de Lenguaje Natural) para explicar la causa raíz del error en lenguaje humano
- **Q4 2025:** Soporte multi-cloud (AWS, Azure, GCP) para infraestructuras híbridas

---

## Licencia y Exención de Responsabilidad

Este proyecto está bajo la licencia MIT.

**Disclaimer:** DockerPulse es una herramienta de prueba de concepto (PoC) para entornos de Hackathon y demostración académica. Aunque utiliza librerías de producción (fastapi, docker-sdk, streamlit), los scripts de inyección de caos deben usarse con precaución en entornos corporativos reales.

---



**DockerPulse** - Del Monitoreo Reactivo a la Auditoría Predictiva

Desarrollado con dedicación por el Equipo de Ingeniería de DockerPulse