<script setup>
import { computed } from 'vue'

// Recibimos los datos de cada contenedor
const props = defineProps({
  nombre: String,
  cpu: Number,
  ram: Number,
  prediccion: String // "CRÍTICO" o "NORMAL"
})

// Lógica para cambiar clase (color) según estrés
const estadoColor = computed(() => {
  if (props.cpu > 80 || props.prediccion === 'CRÍTICO') return 'rojo'
  if (props.cpu > 50) return 'amarillo'
  return 'verde'
})
</script>

<template>
  <div class="card" :class="estadoColor">
    <div class="header">
      <h3>{{ nombre }}</h3>
      <span class="status-dot">●</span>
    </div>

    <div class="metrics">
      <div class="metric">
        <span>CPU</span>
        <div class="progress-bg">
          <div class="progress-fill" :style="{ width: cpu + '%' }"></div>
        </div>
        <span class="value">{{ cpu }}%</span>
      </div>

      <div class="metric">
        <span>RAM</span>
        <div class="progress-bg">
          <div class="progress-fill" :style="{ width: ram + '%' }"></div>
        </div>
        <span class="value">{{ ram }}%</span>
      </div>
    </div>

    <div v-if="prediccion === 'CRÍTICO'" class="alert-box">
      ⚠️ FALLO INMINENTE
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #1e1e1e;
  border-radius: 12px;
  padding: 20px;
  color: #f9fafb;
  border: 1px solid #333;
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.6);
}

/* Colores según estado */
.verde {
  border-top: 4px solid #00ff88;
}
.amarillo {
  border-top: 4px solid #ffcc00;
}
.rojo {
  border-top: 4px solid #ff0055;
  box-shadow: 0 0 15px rgba(255, 0, 85, 0.4);
  animation: pulso 1s infinite;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.header h3 {
  margin: 0;
  font-size: 1rem;
}

.status-dot {
  font-size: 20px;
}

.metrics {
  margin-top: 10px;
}

.metric {
  margin-bottom: 10px;
  font-size: 0.85rem;
}

.progress-bg {
  background: #333;
  height: 8px;
  border-radius: 4px;
  width: 100%;
  margin: 4px 0;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  background: currentColor;
  transition: width 0.5s ease;
}

.value {
  font-size: 0.85rem;
  font-weight: 600;
  float: right;
}

.alert-box {
  background: #ff0055;
  color: white;
  text-align: center;
  padding: 5px;
  border-radius: 4px;
  font-weight: bold;
  margin-top: 10px;
}

@keyframes pulso {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
  }
}
</style>
