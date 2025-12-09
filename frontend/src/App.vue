<script setup>
import { ref, computed } from 'vue'
import ContainerCard from './components/ContainerCard.vue'
import StatusLight from './components/StatusLight.vue'

// 🔹 DATOS FALSOS (mock) por ahora, sin backend
const datos = ref({
  host: { cpu: 37, ram: 62 },
  contenedores: [
    { nombre: 'oracle-db',       cpu: 45, ram: 70, prediccion: 'NORMAL' },
    { nombre: 'nginx-web',       cpu: 82, ram: 40, prediccion: 'CRÍTICO' },
    { nombre: 'redis-cache',     cpu: 15, ram: 20, prediccion: 'NORMAL' },
    { nombre: 'worker-1',        cpu: 65, ram: 55, prediccion: 'NORMAL' },
    { nombre: 'worker-2',        cpu: 90, ram: 80, prediccion: 'CRÍTICO' },
    { nombre: 'monitor-agent',   cpu: 25, ram: 30, prediccion: 'NORMAL' },
    { nombre: 'backup-service',  cpu: 55, ram: 45, prediccion: 'NORMAL' }
  ]
})

// 🔹 Estado global del sistema según los contenedores (solo visual)
const estadoGlobal = computed(() => {
  const conts = datos.value.contenedores

  // Regla simple:
  // - si alguno es CRÍTICO o cpu > 85 → PELIGRO
  // - si alguno tiene cpu > 70 → ADVERTENCIA
  // - si no → OK
  if (conts.some(c => c.prediccion === 'CRÍTICO' || c.cpu > 85)) {
    return 'PELIGRO'
  }
  if (conts.some(c => c.cpu > 70)) {
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
            {{ datos.host.cpu }}%
          </b>
        </div>
        <div class="stat">
          <span>HOST RAM</span>
          <b>{{ datos.host.ram }}%</b>
        </div>
      </div>
    </header>

    <!-- Semáforo global -->
    <StatusLight :estado="estadoGlobal" />

    <!-- Placeholders para futuras gráficas -->
    <section class="charts-placeholder">
      <div class="chart-box">
        <h3>Tendencia de CPU</h3>
        <div class="chart-area">
          <span>Gráfica en tiempo real (pendiente de integración)</span>
        </div>
      </div>
      <div class="chart-box">
        <h3>Tendencia de RAM</h3>
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
    justify-content: space-between;
  }
}
</style>
