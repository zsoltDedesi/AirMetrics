<template>
  <h1>{{ msg }}</h1>

  <n-space vertical>
    <n-card title="DS18B20 Sensor">
      <p>Temperature: {{ formatValue(ds18b20Reading?.temperature, '°C') }}</p>
    </n-card>

    <n-card title="AM2302 Sensor">
      <p>Temperature: {{ formatValue(am2302Reading?.temperature, '°C') }}</p>
      <p>Humidity: {{ formatValue(am2302Reading?.humidity, '%') }}</p>
    </n-card>

    <n-card title="History">
      <h3 class="chart-heading">Sensor History ({{ historyRange }})</h3>
      <LineChartWrapper :since="historyRange" />
    </n-card>

    <n-card title="System Health">
      <p>Backend: {{ isAlive ? 'online' : 'offline' }}</p>
      <p>Stream: {{ isConnected ? 'connected' : 'disconnected' }}</p>
      <p v-if="readiness">Ready: {{ readinessSummary }}</p>
      <p v-if="healthError" class="error-text">Health check failed.</p>
      <p v-if="streamError" class="error-text">Live stream is reconnecting or unavailable.</p>

      <n-space horizontal>
        <n-button type="success" :loading="isChecking" @click="checkSystemHealth">
          Check system health
        </n-button>
      </n-space>
    </n-card>
  </n-space>
</template>

<script setup>
import { computed, onMounted } from 'vue'

import LineChartWrapper from '@/components/LineChartWrapper.vue'
import { useBackendHealth } from '@/composables/useBackendHealth'
import { useSensorStream } from '@/composables/useSensorStream'

defineProps({
  msg: {
    type: String,
    required: true,
  },
})

const historyRange = '12h'

const {
  isAlive,
  readiness,
  isChecking,
  error: healthError,
  checkLiveness,
  checkReadiness,
} = useBackendHealth()

const {
  readings,
  isConnected,
  error: streamError,
  connect,
} = useSensorStream()

const ds18b20Reading = computed(() => readings.value.ds18b20)
const am2302Reading = computed(() => readings.value.am2302)

const readinessSummary = computed(() => {
  if (!readiness.value) {
    return ''
  }

  return Object.entries(readiness.value)
    .map(([name, status]) => `${name}: ${status ? 'ok' : 'fail'}`)
    .join(', ')
})

function formatValue(value, unit) {
  return value == null ? '-' : `${value} ${unit}`
}

async function checkSystemHealth() {
  try {
    await checkReadiness()
  } catch (error) {
    console.error('Error checking system health:', error)
  }
}

onMounted(async () => {
  try {
    await checkLiveness()
  } catch (error) {
    console.error('Backend liveness check failed:', error)
  }

  connect()
})
</script>

<style scoped>
.error-text {
  color: #d03050;
}
</style>
