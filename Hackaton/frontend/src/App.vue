<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import ContainerCard from './components/ContainerCard.vue'
import StatusLight from './components/StatusLight.vue'

// Estado principal
const datos = ref({
  timestamp: null,
  host: { cpu: 0, ram: 0 },
  contenedores: [],
  prediccion: {
    Host_CPU_future: 0,
    nivel_riesgo: 'BAJO'
  },
  anomalia: {
    cluster: 0,
    es_anomalo: false
  }
})

const cargando = ref(true)
const error = ref(null)
let intervalo = null

// === Cargar datos desde el backend ===
async function cargarDatos () {
  try {
    error.value = null

    const res = await fetch('http://localhost:8000/api/status')
    if (!res.ok) {
      throw new Error('Error HTTP ' + res.status)
    }

    const data = await res.json()

    if (data.error) {
      // Si el backend responde con {"error": "..."}
      error.value = data.error
      cargando.value = false
      return
    }

    // Actualizar estado reactivo
    datos.value = {
      timestamp: data.timestamp,
      host: data.host,
      contenedores: data.contenedores || [],
      prediccion: data.prediccion || {
        Host_CPU_future: 0,
        nivel_riesgo: 'BAJO'
      },
      anomalia: data.anomalia || {
        cluster: 0,
        es_anomalo: false
      }
    }

    cargando.value = false
  } catch (e) {
    console.error(e)
    error.value = e.message
    cargando.value = false
  }
}

// === Estado global visual (semáforo) ===
const estadoGlobal = computed(() => {
  const pred = datos.value.prediccion
  const anom = datos.value.anomalia
  const conts = datos.value.contenedores

  // Regla sencilla:
  // - Si hay anomalía o riesgo ALTO -> PELIGRO
  // - Si riesgo MEDIO o algún contenedor con CPU > 70 -> ADVERTENCIA
  // - Si no -> OK
  if (anom?.es_anomalo || pred?.nivel_riesgo === 'ALTO') {
    return 'PELIGRO'
  }

  if (
    pred?.nivel_riesgo === 'MEDIO' ||
    conts.some(c => c.cpu > 70)
  ) {
    return 'ADVERTENCIA'
  }

  return 'OK'
})

// Mensaje de anomalía para el pie de página
const mensajeAnomalia = computed(() => {
  const a = datos.value.anomalia
  if (!a) return 'Análisis de anomalías no disponible.'
  if (a.es_anomalo) {
    return `⚠ Anomalía detectada (cluster ${a.cluster}). Revisar servicios de inmediato.`
  }
  return 'Sin anomalías relevantes detectadas por el modelo no supervisado.'
})

// Texto de riesgo futuro
const textoRiesgo = computed(() => {
  const p = datos.value.prediccion
  if (!p) return ''
  const cpuFutura = p.Host_CPU_future?.toFixed
    ? p.Host_CPU_future.toFixed(2)
    : Number(p.Host_CPU_future || 0).toFixed(2)
  return `CPU futura estimada: ${cpuFutura}%  ·  Nivel de riesgo: ${p.nivel_riesgo}`
})

// Mini métricas para la barra de resumen
const totalContenedores = computed(() => datos.value.contenedores.length)

const contenedoresAltos = computed(() =>
  datos.value.contenedores.filter(c => c.cpu > 70).length
)

// Ciclo de vida: montar / desmontar
onMounted(() => {
  cargarDatos()
  intervalo = setInterval(cargarDatos, 2000) // cada 2s
})

onUnmounted(() => {
  if (intervalo) clearInterval(intervalo)
})
</script>

<template>
  <div class="app-root">
    <div class="dashboard">

      <!-- Barra superior / header -->
      <header class="top-bar">
        <div class="logo-block">
          <div class="logo">
            <span class="logo-icon">🚀</span>
            <span class="logo-text">DOCKER<b>PULSE</b></span>
          </div>
          <span class="tag">PANEL PREDICTIVO DE AIOps</span>
        </div>

        <div class="host-block">
          <div class="stat">
            <span>HOST CPU</span>
            <b :class="{ 'text-danger': datos.host.cpu > 80 }">
              {{ datos.host.cpu.toFixed ? datos.host.cpu.toFixed(1) : datos.host.cpu }}%
            </b>
          </div>
          <div class="divider"></div>
          <div class="stat">
            <span>HOST RAM</span>
            <b>
              {{ datos.host.ram.toFixed ? datos.host.ram.toFixed(1) : datos.host.ram }}%
            </b>
          </div>
        </div>
      </header>

      <!-- Cinta de resumen -->
      <section class="summary-bar" v-if="!cargando">
        <div class="pill">
          <span class="pill-label">Servicios monitoreados</span>
          <span class="pill-value">{{ totalContenedores }}</span>
        </div>

        <div class="pill">
          <span class="pill-label">Riesgo IA</span>
          <span
            class="pill-badge"
            :class="datos.prediccion.nivel_riesgo.toLowerCase()"
          >
            {{ datos.prediccion.nivel_riesgo }}
          </span>
        </div>

        <div class="pill">
          <span class="pill-label">Anomalía</span>
          <span
            class="pill-badge"
            :class="datos.anomalia.es_anomalo ? 'critico' : 'ok'"
          >
            {{ datos.anomalia.es_anomalo ? 'Detectada' : 'Sin anomalías' }}
          </span>
        </div>

        <div class="pill pill-ghost">
          <span class="pill-label">Servicios en alta carga</span>
          <span class="pill-value">
            {{ contenedoresAltos }}
          </span>
        </div>
      </section>

      <section v-else class="summary-bar">
        <div class="pill pill-loading">
          <span class="pill-label">Inicializando motor de IA…</span>
          <span class="loader-dot"></span>
        </div>
      </section>

      <!-- Semáforo global -->
      <StatusLight :estado="estadoGlobal" />

      <!-- Layout principal: izquierda info IA, derecha grid -->
      <section class="main-layout">
        <div class="left-panel">
          <!-- Sección de info de IA -->
          <section class="charts-placeholder">
            <div class="chart-box">
              <h3>Riesgo futuro (IA)</h3>
              <div class="chart-area">
                <span v-if="!cargando">
                  {{ textoRiesgo }}
                </span>
                <span v-else>
                  Calculando predicción de CPU futura...
                </span>
              </div>
            </div>

            <div class="chart-box">
              <h3>Última actualización</h3>
              <div class="chart-area">
                <span v-if="datos.timestamp">
                  Último tick de monitoreo: {{ datos.timestamp }}
                </span>
                <span v-else>
                  Esperando primer paquete de datos...
                </span>
              </div>
            </div>

            <div class="chart-box chart-box-muted">
              <h3>Modo de operación</h3>
              <div class="chart-area chart-area-left">
                <ul class="mini-list">
                  <li>✅ IA supervisada (TensorFlow) para CPU futura</li>
                  <li>✅ IA no supervisada (K-Means) para anomalías</li>
                  <li>✅ Lectura en tiempo real desde Docker + host</li>
                </ul>
              </div>
            </div>
          </section>

          <!-- Mensaje de error si lo hay -->
          <section v-if="error" class="error-box">
            ⚠ Error al obtener datos: {{ error }}
          </section>
        </div>

        <!-- Grid de contenedores -->
        <main class="grid-container">
          <ContainerCard
            v-for="cont in datos.contenedores"
            :key="cont.nombre"
            :nombre="cont.nombre"
            :cpu="Math.round(Math.min(cont.cpu, 100))"
            :ram="Math.round(Math.min(cont.ram, 100))"
            :prediccion="datos.prediccion?.nivel_riesgo === 'ALTO' || datos.anomalia?.es_anomalo ? 'CRÍTICO' : 'NORMAL'"
          />
          <div
            v-if="!cargando && datos.contenedores.length === 0"
            class="empty-state"
          >
            <p>No se han recibido contenedores desde Docker.</p>
            <p class="hint">
              Verifica que el recolector esté apuntando a los contenedores
              configurados.
            </p>
          </div>
        </main>
      </section>

      <!-- Pie de página con anomalías -->
      <footer class="footer">
        <div class="footer-inner">
          <span class="footer-title">Motor de IA DockerPulse</span>
          <span class="footer-text">
            {{ mensajeAnomalia }}
          </span>
        </div>
      </footer>
    </div>
  </div>
</template>

<style>
/* Fondo global oscuro */
body {
  margin: 0;
  background-color: #020617;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
    sans-serif;
  color: #f9fafb;
}

/* Contenedor raíz con fondo tipo panel */
.app-root {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.18), transparent 55%),
    radial-gradient(circle at bottom right, rgba(16, 185, 129, 0.18), transparent 55%),
    #020617;
}

/* Caja del dashboard */
.dashboard {
  width: 100%;
  max-width: 1320px;
  background: radial-gradient(circle at top, #020617 0%, #020617 40%, #020617 100%);
  border-radius: 24px;
  padding: 24px 24px 18px;
  box-shadow:
    0 25px 50px rgba(0, 0, 0, 0.8),
    0 0 0 1px rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(55, 65, 81, 0.8);
  box-sizing: border-box;
}

/* Barra superior estilo industrial */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #020617, #020617);
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid #1f2937;
  margin-bottom: 18px;
  position: relative;
  overflow: hidden;
}

.top-bar::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent, rgba(56, 189, 248, 0.06), transparent);
  pointer-events: none;
}

/* Logo */
.logo-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.35rem;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.logo-icon {
  font-size: 1.4rem;
}

.logo-text {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.logo-text b {
  color: #22d3ee;
}

.tag {
  font-size: 0.68rem;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #9ca3af;
  background: rgba(15, 23, 42, 0.8);
}

/* Stats del host */
.host-block {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 6px 10px;
  border-radius: 999px;
  background: radial-gradient(circle at top left, rgba(15, 23, 42, 0.9), #020617);
  border: 1px solid rgba(31, 41, 55, 0.9);
}

.host-stats {
  display: flex;
  gap: 16px;
  font-size: 0.95rem;
}

.stat span {
  display: block;
  font-size: 0.7rem;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.11em;
}

.stat b {
  font-size: 1.1rem;
}

.divider {
  width: 1px;
  height: 32px;
  background: linear-gradient(to bottom, transparent, #4b5563, transparent);
}

.text-danger {
  color: #fb7185;
  animation: blink 1s infinite;
}

/* Cinta de resumen */
.summary-bar {
  margin-top: 10px;
  margin-bottom: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(31, 41, 55, 0.9);
  font-size: 0.78rem;
}

.pill-ghost {
  background: transparent;
  border-style: dashed;
  border-color: rgba(55, 65, 81, 0.9);
}

.pill-label {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #9ca3af;
  font-size: 0.68rem;
}

.pill-value {
  font-weight: 600;
  font-size: 0.9rem;
}

/* Badge de riesgo/anomalía */
.pill-badge {
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.pill-badge.bajo {
  background: rgba(22, 163, 74, 0.2);
  color: #4ade80;
  border: 1px solid rgba(22, 163, 74, 0.8);
}

.pill-badge.medio {
  background: rgba(234, 179, 8, 0.16);
  color: #facc15;
  border: 1px solid rgba(234, 179, 8, 0.8);
}

.pill-badge.alto,
.pill-badge.critico {
  background: rgba(248, 113, 113, 0.18);
  color: #fb7185;
  border: 1px solid rgba(248, 113, 113, 0.9);
}

.pill-badge.ok {
  background: rgba(34, 197, 94, 0.16);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.9);
}

.pill-loading {
  padding-right: 16px;
}

.loader-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #22d3ee;
  box-shadow: 0 0 8px rgba(34, 211, 238, 0.9);
  animation: pulse-dot 1s infinite;
}

/* Layout principal */
.main-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.4fr);
  gap: 18px;
  margin-top: 10px;
}

/* Panel izquierdo */
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Sección de info IA / bloques */
.charts-placeholder {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.chart-box {
  background: #020617;
  border-radius: 16px;
  border: 1px solid #1f2937;
  padding: 12px 14px;
}

.chart-box h3 {
  margin: 0 0 8px;
  font-size: 0.9rem;
  color: #e5e7eb;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chart-box h3::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #22d3ee;
  box-shadow: 0 0 6px rgba(34, 211, 238, 0.9);
}

.chart-box.chart-box-muted h3::before {
  background: #6b7280;
  box-shadow: none;
}

.chart-area {
  border-radius: 12px;
  border: 1px dashed #4b5563;
  min-height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  color: #9ca3af;
  text-align: center;
  padding: 6px;
}

.chart-area-left {
  justify-content: flex-start;
}

.mini-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.mini-list li {
  font-size: 0.78rem;
  color: #9ca3af;
  margin-bottom: 4px;
}

/* Grid de contenedores (panel derecho) */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 16px;
}

/* Estado vacío */
.empty-state {
  grid-column: 1 / -1;
  background: rgba(15, 23, 42, 0.9);
  border-radius: 14px;
  border: 1px dashed #4b5563;
  padding: 18px;
  text-align: center;
  font-size: 0.85rem;
  color: #9ca3af;
}

.empty-state .hint {
  margin-top: 4px;
  font-size: 0.78rem;
}

/* Error box */
.error-box {
  background: #7f1d1d;
  border: 1px solid #b91c1c;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.85rem;
  margin-top: 4px;
}

/* Footer */
.footer {
  margin-top: 18px;
  padding-top: 10px;
  border-top: 1px solid #1f2937;
}

.footer-inner {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.78rem;
  color: #9ca3af;
}

.footer-title {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

/* Animaciones */
@keyframes blink {
  50% {
    opacity: 0.35;
  }
}

@keyframes pulse-dot {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.4);
    opacity: 0.6;
  }
}

/* Responsive pequeño */
@media (max-width: 900px) {
  .main-layout {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 640px) {
  .app-root {
    padding: 12px;
  }

  .dashboard {
    padding: 16px 14px 12px;
    border-radius: 16px;
  }

  .top-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .host-block {
    align-self: stretch;
    justify-content: space-between;
  }
}
</style>
