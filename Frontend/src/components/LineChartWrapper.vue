<template>

  <BaseLineChart :chart-data="testData" :options="chartOptions" />

</template>



<script setup>
import { computed, onMounted, ref } from 'vue'
import { LineChart as BaseLineChart } from 'vue-chart-3';
import { Chart, registerables } from 'chart.js';

import { getHistory } from '@/api/history';

Chart.register(...registerables);

const props = defineProps({
  since: {
    type: String,
    default: '24h',
  },
});

const HOUR_IN_SECONDS = 3600;
const MINUTE_IN_SECONDS = 60;

function parseSinceToSeconds(value) {
  const rawValue = value.trim().toLowerCase();
  const match = rawValue.match(/^(\d+)([hm])$/);

  if (!match) {
    return null;
  }

  const amount = Number(match[1]);
  const unit = match[2];

  return unit === 'h'
    ? amount * HOUR_IN_SECONDS
    : amount * MINUTE_IN_SECONDS;
}

function getAlignedRange(value) {
  const nowInSeconds = Math.floor(Date.now() / 1000);
  const endTs = Math.floor(nowInSeconds / HOUR_IN_SECONDS) * HOUR_IN_SECONDS;
  const rangeInSeconds = parseSinceToSeconds(value);

  if (!rangeInSeconds) {
    return {
      startTs: null,
      endTs: null,
    };
  }

  return {
    startTs: endTs - rangeInSeconds,
    endTs,
  };
}

const alignedRange = getAlignedRange(props.since);

const filteredDs18b20Data = ref({
  datasets: [
    {
      label: 'Temperature',
      data: [],
      borderColor: 'rgba(75, 192, 192, 1)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      fill: true,
    }]
});


const filteredAm2302Data = ref({});


function formatTimestamp(ts) {
  return new Date(ts * 1000).toLocaleTimeString('hu-HU', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}




onMounted(async () => {
  try {
    const historyData = await getHistory(alignedRange.startTs ?? props.since);
    const measuredData = historyData.readings;

    // console.log("Fetched history data:", measuredData[0]);

    for (const entry of measuredData) {
      if (entry.sensor === "ds18b20") {
        filteredDs18b20Data.value.datasets[0].data.push({
          x: entry.ts,
          y: entry.temperature,
        });
      }
      // if (entry.sensor === "am2302") {
      //   filteredAm2302Data.value.labels.push(formatTimestamp(entry.ts));
      //   filteredAm2302Data.value.datasets[0].data.push(entry.temperature);
      //   filteredAm2302Data.value.datasets[1].data.push(entry.humidity);
      //   console.log("Updated filteredAm2302Data:", filteredAm2302Data);
      // }
    }


    // console.log("Fetched history data:", measuredData);
  } catch (error) {
    console.error("Error fetching history data:", error);
  }
})


const testData = computed(() => ({
  datasets: filteredDs18b20Data.value.datasets,
}));

const chartOptions = {
  responsive: true,
  parsing: false,
  plugins: {
    tooltip: {
      callbacks: {
        title: (items) => {
          const ts = items[0]?.parsed?.x;
          if (typeof ts !== 'number') {
            return '';
          }

          return new Date(ts * 1000).toLocaleString('hu-HU', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
          });
        },
      },
    },
  },
  elements: {
    line: {
      tension: 0.3, // Adjust the tension for smoother curves //
    },
  },
  scales: {
    x: {
      type: 'linear',
      min: alignedRange.startTs ?? undefined,
      max: alignedRange.endTs ?? undefined,
      ticks: {
        stepSize: HOUR_IN_SECONDS,
        callback: (value) => formatTimestamp(Number(value)),
      },
    },
    y: {
      beginAtZero: false,
    },
  },
};

</script>
