<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import ContainerCard from './components/ContainerCard.vue'
import StatusLight from './components/StatusLight.vue'

// Estado principal que vendrá del backend
const datos = ref({
  host: { cpu: 0, ram: 0 },
  contenedores: [],
  prediccion: { Host_CPU_future: 0, nivel_riesgo: 'BAJO' },
  anomalia: { cluster: 0, es_anomalo: false },
  timestamp: null
})

const cargando = ref(true)
const error = ref(null)
let intervalo = null

// 🔹 Llamada al backend FastAPI
async function cargarDatos() {
  try {
    error.value = null
    const res = await fetch('http://localhost:8000/api/status')
    if (!res.ok) throw new Error('Error HTTP ' + res.status)

    const data = await res.json()

    // Mapear contenedores para que cada uno tenga 'prediccion'
    const contenedores = (data.contenedores || []).map(c => {
      let pred = 'NORMAL'
      if (c.cpu > 85) pred = 'CRÍTICO'
      else if (c.cpu > 70) pred = 'ALTO'
      return {
        nombre: c.nombre,
        cpu: c.cpu,
        ram: c.ram,
        prediccion: pred
      }
    })

    datos.value = {
      host: data.host,
      contenedores,
      prediccion: data.prediccion,
      anomalia: data.anomalia,
      timestamp: data.timestamp
    }

    cargando.value = false
  } catch (e) {
    console.error(e)
    error.value = e.message
    cargando.value = false
  }
}

// 🔹 Arrancamos el polling
onMounted(() => {
  cargarDatos()
  intervalo = setInterval(cargarDatos, 2000) // cada 2s
})

onUnmounted(() => {
  if (intervalo) clearInterval(intervalo)
})

// 🔹 Estado global del sistema
const estadoGlobal = computed(() => {
  const d = datos.value
  const conts = d.contenedores || []

  // Usamos:
  // - nivel_riesgo de la predicción
  // - CPU de contenedores
  // - flag de anomalía
  if (
    d.prediccion?.nivel_riesgo === 'ALTO' ||
    d.anomalia?.es_anomalo ||
    conts.some(c => c.prediccion === 'CRÍTICO' || c.cpu > 85)
  ) {
    return 'PELIGRO'
  }

  if (
    d.prediccion?.nivel_riesgo === 'MEDIO' ||
    conts.some(c => c.cpu > 70)
  ) {
    return 'ADVERTENCIA'
  }

  return 'OK'
})
</script>

<template>
  <div class="dashboard">
    <!-- Barra superior / header -->
    <header class="top-bar">
      <div class="logo">
        🚀 DOCKER<b>PULSE</b>
        <span class="tag">PANEL PREDICTIVO</span>
      </div>

      <div class="host-stats">
        <div class="stat">
          <span>HOST CPU</span>
          <b :class="{ 'text-danger': datos.host.cpu > 80 }">
            {{ datos.host.cpu.toFixed(1) }}%
          </b>
        </div>
        <div class="stat">
          <span>HOST RAM</span>
          <b>{{ datos.host.ram.toFixed(1) }}%</b>
        </div>
        <div class="stat">
          <span>CPU FUTURA (IA)</span>
          <b :class="{ 'text-danger': datos.prediccion.Host_CPU_future >= 80 }">
            {{ datos.prediccion.Host_CPU_future.toFixed(1) }}%
          </b>
        </div>
      </div>
    </header>

    <!-- Semáforo global -->
    <StatusLight :estado="estadoGlobal" />

    <!-- Mensajes de carga / error -->
    <section v-if="error" class="info-box error">
      ❌ Error al obtener datos: {{ error }}
    </section>

    <section v-else-if="cargando" class="info-box loading">
      ⏳ Cargando datos en tiempo real desde DockerPulse...
    </section>

    <section v-else>
      <!-- Placeholders para futuras gráficas -->
      <section class="charts-placeholder">
        <div class="chart-box">
          <h3>Tendencia de CPU (Host)</h3>
          <div class="chart-area">
            <span>Gráfica en tiempo real (pendiente de integración)</span>
          </div>
        </div>
        <div class="chart-box">
          <h3>Tendencia de RAM (Host)</h3>
          <div class="chart-area">
            <span>Gráfica en tiempo real (pendiente de integración)</span>
          </div>
        </div>
      </section>

      <!-- Grid de contenedores -->
      <main class="grid-container">
        <ContainerCard
          v-for="cont in datos.contenedores"
          :key="cont.nombre"
          :nombre="cont.nombre"
          :cpu="cont.cpu"
          :ram="cont.ram"
          :prediccion="cont.prediccion"
        />
      </main>

      <!-- Pie con timestamp y anomalías -->
      <footer class="footer-info">
        <span>Última actualización: {{ datos.timestamp }}</span>
        <span v-if="datos.anomalia?.es_anomalo" class="anomalia">
          🔴 Anomalía detectada (cluster {{ datos.anomalia.cluster }})
        </span>
        <span v-else class="anomalia ok">
          🟢 Sin anomalías detectadas por K-Means
        </span>
      </footer>
    </section>
  </div>
</template>

<style>
/* Fondo global oscuro */
body {
  margin: 0;
  background-color: #0b0f19;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
    sans-serif;
  color: #f9fafb;
}

.dashboard {
  padding: 24px;
}

/* Barra superior estilo industrial */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #111827;
  padding: 16px 24px;
  border-radius: 16px;
  border-bottom: 2px solid #00d2ff;
  margin-bottom: 28px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
}

.logo {
  font-size: 1.4rem;
  letter-spacing: 2px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo b {
  color: #00d2ff;
}

.tag {
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #00d2ff;
  text-transform: uppercase;
}

/* Stats del host */
.host-stats {
  display: flex;
  gap: 24px;
  font-size: 0.95rem;
}

.stat span {
  display: block;
  font-size: 0.75rem;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stat b {
  font-size: 1.2rem;
}

.text-danger {
  color: #ff0055;
  animation: blink 1s infinite;
}

/* Mensajes info */
.info-box {
  margin-bottom: 20px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.9rem;
}

.info-box.loading {
  background: #020617;
  border: 1px solid #1f2937;
}

.info-box.error {
  background: #450a0a;
  border: 1px solid #b91c1c;
}

/* Placeholders para gráficas */
.charts-placeholder {
  margin-top: 10px;
  margin-bottom: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.chart-box {
  background: #020617;
  border-radius: 16px;
  border: 1px solid #1f2937;
  padding: 14px 16px;
}

.chart-box h3 {
  margin: 0 0 10px;
  font-size: 0.95rem;
  color: #9ca3af;
}

.chart-area {
  border-radius: 12px;
  border: 1px dashed #4b5563;
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  color: #6b7280;
}

/* Grid de contenedores */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

/* Footer */
.footer-info {
  margin-top: 20px;
  font-size: 0.8rem;
  display: flex;
  justify-content: space-between;
  color: #9ca3af;
}

.footer-info .anomalia {
  font-weight: 600;
}

.footer-info .anomalia.ok {
  color: #22c55e;
}

/* Animación para estado crítico del host */
@keyframes blink {
  50% {
    opacity: 0.4;
  }
}

/* Responsive pequeño */
@media (max-width: 640px) {
  .dashboard {
    padding: 16px;
  }

  .top-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .host-stats {
    width: 100%;
    flex-wrap: wrap;
    justify-content: flex-start;
    row-gap: 8px;
  }

  .footer-info {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
