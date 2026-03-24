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

const filteredDs18b20Data = ref({
  labels: [], // Timestamps will go here
  datasets: [
    {
      label: 'Temperature',
      data: [], // Temperature values will go here
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
  });
}




onMounted(async () => {
  try {
    const historyData = await getHistory(props.since);
    const measuredData = historyData.readings;

    // console.log("Fetched history data:", measuredData[0]);

    for (const entry of measuredData) {
      if (entry.sensor === "ds18b20") {

        filteredDs18b20Data.value.labels.push(formatTimestamp(entry.ts));
        filteredDs18b20Data.value.datasets[0].data.push(entry.temperature);
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
  labels: filteredDs18b20Data.value.labels,
  datasets: filteredDs18b20Data.value.datasets,
}));

const chartOptions = {
  responsive: true,
  elements: {
    line: {
      tension: 0.3, // Adjust the tension for smoother curves //
    },
  },
  scales: {
    y: {
      beginAtZero: false,
    },
  },
};

</script>
