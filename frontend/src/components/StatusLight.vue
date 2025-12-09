<script setup>
import { computed } from 'vue'

const props = defineProps({
  estado: {
    type: String,
    default: 'OK' // 'OK' | 'ADVERTENCIA' | 'PELIGRO'
  }
})

const colorClass = computed(() => {
  if (props.estado === 'PELIGRO') return 'rojo'
  if (props.estado === 'ADVERTENCIA') return 'amarillo'
  return 'verde'
})

const label = computed(() => {
  if (props.estado === 'PELIGRO') return 'PELIGRO'
  if (props.estado === 'ADVERTENCIA') return 'ADVERTENCIA'
  return 'ESTABLE'
})
</script>

<template>
  <section class="status-wrapper">
    <div>
      <h2>Estado general del sistema</h2>
      <p class="subtitle">Análisis global de carga de contenedores</p>
    </div>

    <div class="semaforo">
      <div class="circle" :class="colorClass"></div>
      <div class="text">
        <span class="label">{{ label }}</span>
        <span class="hint">
          {{ estado === 'PELIGRO'
            ? 'Revisar contenedores críticos'
            : estado === 'ADVERTENCIA'
              ? 'Cargas altas en algunos servicios'
              : 'Operación normal' }}
        </span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.status-wrapper {
  margin-top: 20px;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #020617;
  border-radius: 16px;
  border: 1px solid #1f2937;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

h2 {
  margin: 0;
  font-size: 1.05rem;
}

.subtitle {
  margin: 4px 0 0;
  font-size: 0.85rem;
  color: #9ca3af;
}

.semaforo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.circle {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  background: #4b5563;
  box-shadow: 0 0 0 2px #111827;
}

.circle.verde {
  background: #22c55e;
  box-shadow: 0 0 16px rgba(34, 197, 94, 0.7);
}

.circle.amarillo {
  background: #facc15;
  box-shadow: 0 0 16px rgba(250, 204, 21, 0.7);
}

.circle.rojo {
  background: #ef4444;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.9);
  animation: parpadeo 1s infinite;
}

.text {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hint {
  font-size: 0.8rem;
  color: #9ca3af;
}

@keyframes parpadeo {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

@media (max-width: 640px) {
  .status-wrapper {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
