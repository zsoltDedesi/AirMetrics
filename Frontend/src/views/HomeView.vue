<template>
  <main class="dashboard-shell">
    <section class="dashboard-header" aria-label="AirMetrics status">
      <div class="brand-mark">
        <n-icon size="26">
          <Home24Regular />
        </n-icon>
      </div>
      <div class="brand-copy">
        <h1>AirMetrics</h1>
        <p>Local temperature & humidity monitor</p>
      </div>
      <div class="header-pills">
        <span class="pill pill-live">Live</span>
        <span class="pill pill-connected">
          <n-icon size="15">
            <Wifi124Regular />
          </n-icon>
          {{ streamStatusText }}
        </span>
        <span class="pill pill-host">raspberrypi.local</span>
      </div>
    </section>

    <section class="metric-grid" aria-label="Latest sensor readings">
      <article
        v-for="metric in metricCards"
        :key="metric.key"
        class="metric-card"
        :class="[`metric-card-${metric.tone}`, { 'metric-card-muted': !metric.reading }]"
      >
        <div class="metric-card-accent" aria-hidden="true"></div>
        <div class="metric-icon">
          <n-icon size="22">
            <component :is="metric.icon" />
          </n-icon>
        </div>
        <div class="metric-title">{{ metric.title }}</div>
        <div class="metric-sensor">Sensor: {{ metric.sensorLabel }}</div>
        <div class="metric-value">
          <span>{{ metric.value }}</span>
          <small>{{ metric.unit }}</small>
        </div>
        <div class="metric-footer">
          <span>Updated: {{ metric.updatedAt }}</span>
          <span class="state-badge" :class="metric.badgeClass">{{ metric.badge }}</span>
        </div>
      </article>
    </section>

    <section class="status-strip" aria-label="System health summary">
      <article
        v-for="item in statusItems"
        :key="item.label"
        class="status-tile"
        :class="`status-tile-${item.tone}`"
      >
        <span class="status-icon">
          <n-icon size="18">
            <component :is="item.icon" />
          </n-icon>
        </span>
        <span>
          <small>{{ item.label }}</small>
          <strong>{{ item.value }}</strong>
        </span>
      </article>
    </section>

    <section class="toolbar-panel" aria-label="History controls">
      <div class="time-range-control">
        <span>Time range</span>
        <div class="segmented-control" role="group" aria-label="Select history range">
          <button
            v-for="range in historyRanges"
            :key="range.value"
            type="button"
            :class="{ active: historyRange === range.value }"
            @click="historyRange = range.value"
          >
            {{ range.label }}
          </button>
        </div>
      </div>

      <div class="toolbar-actions">
        <span class="event-badge">
          <n-icon size="15">
            <DataUsage24Regular />
          </n-icon>
          Event-based
        </span>
        <button type="button" class="toolbar-button" @click="exportHistoryCsv">
          <n-icon size="17">
            <ArrowDownload24Regular />
          </n-icon>
          CSV
        </button>
        <button type="button" class="toolbar-button" title="Threshold settings are backend-managed.">
          <n-icon size="17">
            <Settings24Regular />
          </n-icon>
          Thresholds
        </button>
      </div>
    </section>

    <section class="chart-grid" aria-label="History charts">
      <article class="chart-card">
        <header class="chart-card-header">
          <div>
            <h2>Temperature history</h2>
            <p>Last {{ historyRangeLabel }} · event-sampled readings</p>
          </div>
          <div class="chart-legend">
            <span><i class="legend-dot legend-ds18b20"></i>DS18B20</span>
            <span><i class="legend-dot legend-am2302"></i>AM2302</span>
          </div>
        </header>
        <LineChartWrapper :since="historyRange" metric="temperature" />
      </article>

      <article class="chart-card">
        <header class="chart-card-header">
          <div>
            <h2>Humidity history</h2>
            <p>Last {{ historyRangeLabel }} · event-sampled readings</p>
          </div>
          <div class="chart-legend">
            <span><i class="legend-dot legend-humidity"></i>AM2302 humidity</span>
          </div>
        </header>
        <LineChartWrapper :since="historyRange" metric="humidity" />
      </article>
    </section>

    <section class="notice-grid" aria-label="Dashboard messages">
      <article class="notice-card notice-warning">
        <n-icon size="18">
          <Warning24Regular />
        </n-icon>
        <p><strong>Warning state:</strong> thresholds can surface here without interrupting the dashboard.</p>
      </article>
      <article class="notice-card notice-error">
        <n-icon size="18">
          <CloudOff24Regular />
        </n-icon>
        <p><strong>Sensor offline:</strong> metric cards switch to muted values and offline badges.</p>
      </article>
      <article class="notice-card notice-empty">
        <n-icon size="18">
          <Drop24Regular />
        </n-icon>
        <p><strong>No data yet:</strong> charts reserve space and show an empty-state message.</p>
      </article>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  ArrowDownload24Regular,
  ArrowSync24Regular,
  CheckmarkCircle24Regular,
  CloudOff24Regular,
  DataUsage24Regular,
  Database24Regular,
  Drop24Regular,
  Home24Regular,
  Pulse24Regular,
  Settings24Regular,
  Temperature24Regular,
  Warning24Regular,
  Wifi124Regular,
} from '@vicons/fluent'

import LineChartWrapper from '@/components/LineChartWrapper.vue'
import { getHistory } from '@/api/history'
import { getSystemStatus } from '@/api/system'
import { useBackendHealth } from '@/composables/useBackendHealth'
import { useSensorStream } from '@/composables/useSensorStream'
import { getAlignedRange } from '@/utils/timeRange'

const historyRange = ref('24h')
const systemStatus = ref(null)
const systemStatusError = ref(null)
const nowTs = ref(Math.floor(Date.now() / 1000))
let statusTimerId = null
const historyRanges = [
  { label: '1h', value: '1h' },
  { label: '6h', value: '6h' },
  { label: '24h', value: '24h' },
]

const {
  isAlive,
  readiness,
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
const ds18b20Ready = computed(() => readiness.value?.ds18b20 === true)
const am2302Ready = computed(() => readiness.value?.am2302 === true)

const historyRangeLabel = computed(() => historyRanges.find((range) => range.value === historyRange.value)?.label ?? historyRange.value)
const streamStatusText = computed(() => (isConnected.value ? 'Connected' : 'Disconnected'))
const lastCleanupText = computed(() => {
  if (systemStatusError.value) {
    return 'Unavailable'
  }

  return formatRelativeTimestamp(systemStatus.value?.last_cleanup_ts)
})
const retentionText = computed(() => {
  const retentionHours = systemStatus.value?.retention_hours
  if (retentionHours == null) {
    return '--'
  }

  return `${retentionHours}h`
})

const metricCards = computed(() => [
  createMetricCard({
    key: 'ds18b20-temperature',
    title: 'DS18B20 Temperature',
    sensorLabel: 'ds18b20',
    sensorReady: ds18b20Ready.value,
    reading: ds18b20Reading.value,
    value: ds18b20Reading.value?.temperature,
    unit: '°C',
    icon: Temperature24Regular,
    tone: 'warm',
  }),
  createMetricCard({
    key: 'am2302-temperature',
    title: 'AM2302 Temperature',
    sensorLabel: 'am2302_temp',
    sensorReady: am2302Ready.value,
    reading: am2302Reading.value,
    value: am2302Reading.value?.temperature,
    unit: '°C',
    icon: Temperature24Regular,
    tone: 'warm',
  }),
  createMetricCard({
    key: 'am2302-humidity',
    title: 'AM2302 Humidity',
    sensorLabel: 'am2302_hum',
    sensorReady: am2302Ready.value,
    reading: am2302Reading.value,
    value: am2302Reading.value?.humidity,
    unit: '%',
    icon: Drop24Regular,
    tone: 'cool',
  }),
])

const statusItems = computed(() => [
  {
    label: 'Backend',
    value: isAlive.value ? 'Healthy' : 'Offline',
    icon: CheckmarkCircle24Regular,
    tone: isAlive.value ? 'ok' : 'warn',
  },
  {
    label: 'SSE Stream',
    value: streamStatusText.value,
    icon: DataUsage24Regular,
    tone: isConnected.value ? 'ok' : 'warn',
  },
  {
    label: 'Retention',
    value: retentionText.value,
    icon: ArrowSync24Regular,
    tone: 'neutral',
  },
  {
    label: 'Database',
    value: readiness.value?.db === false ? 'Issue' : 'SQLite',
    icon: Database24Regular,
    tone: readiness.value?.db === false ? 'warn' : 'info',
  },
  {
    label: 'Last cleanup',
    value: lastCleanupText.value,
    icon: Pulse24Regular,
    tone: systemStatusError.value ? 'warn' : 'neutral',
  },
  {
    label: 'AM2302 errors',
    value: streamError.value || healthError.value ? 'Check stream' : '0 recent',
    icon: Warning24Regular,
    tone: streamError.value || healthError.value ? 'warn' : 'notice',
  },
])

function createMetricCard({ key, title, sensorLabel, sensorReady, reading, value, unit, icon, tone }) {
  const hasValue = value != null
  const online = Boolean(sensorReady && isConnected.value)

  return {
    key,
    title,
    sensorLabel,
    reading,
    value: hasValue ? formatNumber(value) : '--',
    unit,
    icon,
    tone,
    updatedAt: reading?.ts ? formatTimeWithSeconds(reading.ts) : '--:--:--',
    badge: online ? 'Online' : sensorReady ? 'Waiting' : 'Offline',
    badgeClass: online ? 'state-online' : sensorReady ? 'state-waiting' : 'state-offline',
  }
}

function formatNumber(value) {
  return Number(value).toLocaleString('en-US', {
    maximumFractionDigits: 1,
    minimumFractionDigits: Number.isInteger(value) ? 0 : 1,
  })
}

function formatTimeWithSeconds(ts) {
  return new Date(ts * 1000).toLocaleTimeString('hu-HU', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

function formatRelativeTimestamp(ts) {
  if (!ts) {
    return 'Pending'
  }

  const diffSeconds = Math.max(0, nowTs.value - ts)
  if (diffSeconds < 60) {
    return 'Just now'
  }

  const diffMinutes = Math.floor(diffSeconds / 60)
  if (diffMinutes < 60) {
    return `${diffMinutes} min ago`
  }

  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) {
    return `${diffHours} h ago`
  }

  return `${Math.floor(diffHours / 24)} d ago`
}

async function refreshSystemStatus() {
  try {
    systemStatus.value = await getSystemStatus()
    systemStatusError.value = null
  } catch (error) {
    systemStatusError.value = error
    console.error('System status check failed:', error)
  }
}

function csvEscape(value) {
  if (value == null) {
    return ''
  }

  return `"${String(value).replaceAll('"', '""')}"`
}

async function exportHistoryCsv() {
  const range = getAlignedRange(historyRange.value)
  const historyData = await getHistory(range.startTs ?? historyRange.value)
  const rows = [
    ['sensor', 'temperature', 'humidity', 'timestamp'],
    ...(historyData.readings ?? []).map((entry) => [
      entry.sensor,
      entry.temperature,
      entry.humidity,
      new Date(entry.ts * 1000).toISOString(),
    ]),
  ]

  const csv = rows.map((row) => row.map(csvEscape).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = `airmetrics-history-${historyRange.value}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  try {
    await Promise.all([checkLiveness(), checkReadiness(), refreshSystemStatus()])
  } catch (error) {
    console.error('Backend health check failed:', error)
  }

  connect()
  statusTimerId = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000)
    checkReadiness()
    refreshSystemStatus()
  }, 60_000)
})

onUnmounted(() => {
  if (statusTimerId != null) {
    window.clearInterval(statusTimerId)
  }
})
</script>
