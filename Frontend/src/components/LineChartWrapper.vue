<template>
  <p v-if="isLoading">Loading history...</p>
  <p v-else-if="error" class="error-text">Failed to load history.</p>
  <BaseLineChart v-else :chart-data="chartData" :options="chartOptions" />
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { LineChart as BaseLineChart } from 'vue-chart-3'
import { Chart, registerables } from 'chart.js'

import { getHistory } from '@/api/history'
import {
  HOUR_IN_SECONDS,
  formatDateTimeLabel,
  formatTimeLabel,
  getAlignedRange,
} from '@/utils/timeRange'

Chart.register(...registerables)

const props = defineProps({
  since: {
    type: String,
    default: '24h',
  },
})

const readings = ref([])
const isLoading = ref(false)
const error = ref(null)

const alignedRange = computed(() => getAlignedRange(props.since))

const ds18b20Points = computed(() =>
  readings.value
    .filter((entry) => entry.sensor === 'ds18b20')
    .map((entry) => ({
      x: entry.ts,
      y: entry.temperature,
    })),
)

const chartData = computed(() => ({
  datasets: [
    {
      label: 'DS18B20 temperature',
      data: ds18b20Points.value,
      borderColor: 'rgba(75, 192, 192, 1)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      fill: true,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  parsing: false,
  plugins: {
    tooltip: {
      callbacks: {
        title: (items) => {
          const ts = items[0]?.parsed?.x
          return typeof ts === 'number' ? formatDateTimeLabel(ts) : ''
        },
      },
    },
  },
  elements: {
    line: {
      tension: 0.3,
    },
  },
  scales: {
    x: {
      type: 'linear',
      min: alignedRange.value.startTs ?? undefined,
      max: alignedRange.value.endTs ?? undefined,
      ticks: {
        stepSize: HOUR_IN_SECONDS,
        callback: (value) => formatTimeLabel(Number(value)),
      },
    },
    y: {
      beginAtZero: false,
    },
  },
}))

async function loadHistory() {
  isLoading.value = true
  error.value = null

  try {
    const range = alignedRange.value
    const historyData = await getHistory(range.startTs ?? props.since)
    readings.value = historyData.readings ?? []
  } catch (historyError) {
    error.value = historyError
    console.error('Error fetching history data:', historyError)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadHistory)
watch(() => props.since, loadHistory)
</script>

<style scoped>
.error-text {
  color: #d03050;
}
</style>
