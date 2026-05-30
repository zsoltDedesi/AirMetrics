<template>
  <div class="chart-surface">
    <p v-if="isLoading" class="chart-state">Loading history...</p>
    <p v-else-if="error" class="chart-state chart-error">Failed to load history.</p>
    <p v-else-if="!hasData" class="chart-state">No data yet.</p>
    <template v-else>
      <VChart class="history-chart" :option="chartOptions" autoresize />
      <span v-if="hiddenOutlierCount > 0" class="chart-outlier-badge">
        {{ hiddenOutlierLabel }}
      </span>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

import { getHistory } from '@/api/history'
import {
  formatDateTimeLabel,
  formatTimeLabel,
  getAlignedRange,
} from '@/utils/timeRange'

use([
  CanvasRenderer,
  GridComponent,
  LineChart,
  TooltipComponent,
])

const TEMPERATURE_DISPLAY_RANGE = {
  min: -40,
  max: 85,
}

const props = defineProps({
  since: {
    type: String,
    default: '24h',
  },
  metric: {
    type: String,
    default: 'temperature',
    validator: (value) => ['temperature', 'humidity'].includes(value),
  },
})

const readings = ref([])
const isLoading = ref(false)
const error = ref(null)

const alignedRange = computed(() => getAlignedRange(props.since))

const ds18b20TemperaturePoints = computed(() =>
  readings.value
    .filter((entry) => entry.sensor === 'ds18b20' && isDisplayableTemperature(entry.temperature))
    .map(toTemperaturePoint),
)

const am2302TemperaturePoints = computed(() =>
  readings.value
    .filter((entry) => entry.sensor === 'am2302' && isDisplayableTemperature(entry.temperature))
    .map(toTemperaturePoint),
)

const am2302HumidityPoints = computed(() =>
  readings.value
    .filter((entry) => entry.sensor === 'am2302' && entry.humidity != null)
    .map((entry) => [entry.ts * 1000, entry.humidity]),
)

const hasData = computed(() =>
  props.metric === 'humidity'
    ? am2302HumidityPoints.value.length > 0
    : ds18b20TemperaturePoints.value.length > 0 || am2302TemperaturePoints.value.length > 0,
)

const hiddenOutlierCount = computed(() => {
  if (props.metric !== 'temperature') {
    return 0
  }

  return readings.value.filter((entry) =>
    (entry.sensor === 'ds18b20' || entry.sensor === 'am2302')
      && entry.temperature != null
      && !isDisplayableTemperature(entry.temperature),
  ).length
})

const hiddenOutlierLabel = computed(() =>
  hiddenOutlierCount.value === 1
    ? '1 outlier hidden'
    : `${hiddenOutlierCount.value} outliers hidden`,
)

const chartColors = computed(() => ({
  ds18b20: getCssToken('--md-sys-color-tertiary', '#805600'),
  am2302: getCssToken('--md-sys-color-error', '#ba1a1a'),
  humidity: getCssToken('--md-sys-color-secondary', '#4a6365'),
  humidityFill: getCssToken('--md-sys-color-secondary-container', '#cce8ea'),
  tooltip: getCssToken('--md-sys-color-inverse-surface', '#2b3132'),
  tooltipText: getCssToken('--md-sys-color-inverse-on-surface', '#edf2f3'),
  tick: getCssToken('--md-sys-color-on-surface-variant', '#3f494a'),
  grid: getCssToken('--md-sys-color-outline-variant', '#bec8c9'),
}))

const chartOptions = computed(() => ({
  animation: false,
  color: props.metric === 'humidity'
    ? [chartColors.value.humidity]
    : [chartColors.value.ds18b20, chartColors.value.am2302],
  grid: {
    top: hiddenOutlierCount.value > 0 ? 42 : 22,
    right: 12,
    bottom: 8,
    left: 8,
    containLabel: true,
  },
  tooltip: {
    trigger: 'axis',
    confine: true,
    backgroundColor: chartColors.value.tooltip,
    borderWidth: 0,
    textStyle: {
      color: chartColors.value.tooltipText,
    },
    valueFormatter: (value) => formatMetricValue(value),
  },
  xAxis: {
    type: 'time',
    min: alignedRange.value.startTs ? alignedRange.value.startTs * 1000 : undefined,
    max: alignedRange.value.endTs ? alignedRange.value.endTs * 1000 : undefined,
    boundaryGap: false,
    axisLine: {
      lineStyle: {
        color: chartColors.value.grid,
      },
    },
    axisTick: {
      show: false,
    },
    axisLabel: {
      color: chartColors.value.tick,
      hideOverlap: true,
      formatter: (value) => formatTimeLabel(Math.floor(value / 1000)),
    },
    splitLine: {
      show: false,
    },
  },
  yAxis: {
    type: 'value',
    scale: true,
    axisLabel: {
      color: chartColors.value.tick,
      formatter: (value) => `${value}${props.metric === 'humidity' ? '%' : '°'}`,
    },
    splitLine: {
      lineStyle: {
        color: chartColors.value.grid,
        type: 'dashed',
      },
    },
  },
  series: props.metric === 'humidity'
    ? [
        createSeries({
          name: 'AM2302 humidity',
          data: am2302HumidityPoints.value,
          color: chartColors.value.humidity,
          areaColor: chartColors.value.humidityFill,
        }),
      ]
    : [
        createSeries({
          name: 'DS18B20',
          data: ds18b20TemperaturePoints.value,
          color: chartColors.value.ds18b20,
        }),
        createSeries({
          name: 'AM2302',
          data: am2302TemperaturePoints.value,
          color: chartColors.value.am2302,
        }),
      ],
}))

function createSeries({ name, data, color, areaColor = null }) {
  return {
    name,
    type: 'line',
    data,
    smooth: true,
    showSymbol: false,
    clip: true,
    sampling: 'lttb',
    lineStyle: {
      width: 3,
      color,
    },
    areaStyle: areaColor
      ? {
          color: areaColor,
          opacity: 0.7,
        }
      : undefined,
    emphasis: {
      focus: 'series',
    },
  }
}

function toTemperaturePoint(entry) {
  return [entry.ts * 1000, entry.temperature]
}

function isDisplayableTemperature(value) {
  return Number.isFinite(value)
    && value >= TEMPERATURE_DISPLAY_RANGE.min
    && value <= TEMPERATURE_DISPLAY_RANGE.max
}

function formatMetricValue(value) {
  if (value == null) {
    return ''
  }

  const unit = props.metric === 'humidity' ? '%' : '°C'
  return `${Number(value).toFixed(1)}${unit}`
}

function getCssToken(name, fallback) {
  if (typeof window === 'undefined') {
    return fallback
  }

  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback
}

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
watch(() => [props.since, props.metric], loadHistory)
</script>

<style scoped>
.chart-surface {
  position: relative;
  height: 280px;
  margin-top: 22px;
  padding: 0;
  overflow: hidden;
  border-radius: var(--md-sys-shape-corner-large);
  background: var(--md-sys-color-surface-container-lowest);
}

.history-chart {
  width: 100%;
  height: 100%;
}

.chart-outlier-badge {
  position: absolute;
  top: 4px;
  right: 8px;
  max-width: calc(100% - 16px);
  padding: 5px 10px;
  overflow: hidden;
  border: 1px solid var(--md-sys-color-tertiary-container);
  border-radius: var(--md-sys-shape-corner-extra-large);
  background: var(--md-sys-color-tertiary-container);
  color: var(--md-sys-color-on-tertiary-container);
  font-size: var(--md-sys-typescale-label-medium-size);
  font-weight: 700;
  line-height: var(--md-sys-typescale-label-medium-line-height);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chart-state {
  display: grid;
  min-height: 280px;
  margin: 0;
  place-items: center;
  color: var(--md-sys-color-on-surface-variant);
  font-size: var(--md-sys-typescale-body-medium-size);
  line-height: var(--md-sys-typescale-body-medium-line-height);
  font-weight: 700;
}

.chart-error {
  color: var(--md-sys-color-error);
}

@media (max-width: 720px) {
  .chart-surface {
    height: 230px;
  }

  .chart-state {
    min-height: 230px;
  }
}
</style>
