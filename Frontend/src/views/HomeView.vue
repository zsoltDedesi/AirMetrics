<template>
  <h1>{{ msg }}</h1>

  <!-- <p>Status: {{ status }}</p> -->
  <n-space vertical>
    <n-card title="DS18B20 Sensor">
      <p>Temperature: {{ Ds18b20Temperature ?? '-' }} °C</p>
    </n-card>

    <n-card title="AM2302 Sensor"> 
      <p>Temperature: {{ Am2302Temperature ?? '-' }} °C</p>
      <p>Humidity: {{ Am2302Humidity ?? '-' }} %</p>
    </n-card>
    

    <n-card title="History">
      <h3 class="chart-heading">Szenzor History ( {{timestamp}} )</h3>
      <line-chart-wrapper v-bind:since='timestamp' />
      <!-- <LineChart :chart-data="testData" :options="chartOptions" /> -->
    </n-card>


    <n-card title="System Health">
      <p>Click the button below to check if the system is healthy.</p>
      <n-space horizontal>

        <!-- <n-button type="primary" @click="fetchHistory">Fetch history data</n-button> -->
        <n-button type="success" @click="checkSystemHealth">Check system health</n-button>
      </n-space>
    </n-card>
  </n-space>
</template>


<script setup>
import { ref, onMounted, onBeforeUnmount} from 'vue'
import { getBackendIsAlive, systemIsHealthy } from '@/api/health';
import LineChartWrapper from '@/components/LineChartWrapper.vue';


defineProps({
  msg: String,

})

// const status = ref("Connecting...");

const Ds18b20Temperature = ref(null);
const Am2302Temperature = ref(null);
const Am2302Humidity = ref(null);
const timestamp = "12h"; // Default to last hours, can be made dynamic later

let eventSource = null;


onMounted(async() => {
  const isAlive = await getBackendIsAlive();
  console.log("Backend is alive:", isAlive);

  eventSource = new EventSource(`${import.meta.env.VITE_API_BASE_BACKEND_URL}/stream`);
  eventSource.addEventListener ('reading', (event) => {
    try {

      const data = JSON.parse(event.data);
      console.log("Received SSE data:", data);
      if (data.sensor === "ds18b20") {
        Ds18b20Temperature.value = data.temperature;

      } else if (data.sensor === "am2302") {
         Am2302Temperature.value = data.temperature;
        Am2302Humidity.value = data.humidity;
      }
    } catch (error) {
      console.error("Invalid SSE data received:", error);
    }
  });

  eventSource.onerror = (event) => {
    console.error("SSE connection error:", event);
    // status.value = "reconnecting...";
  }

})

onBeforeUnmount(() => {
  if (eventSource) {
    eventSource.close();
  }
})

const checkSystemHealth = async () => {
  try {
    const isHealthy = await systemIsHealthy();
    console.log("System is healthy:", isHealthy);
    // alert(`System is healthy: ${JSON.stringify(isHealthy)}`);
  } catch (error) {
    console.error("Error checking system health:", error);
    alert("Failed to check system health. See console for details.");
  }
}




</script>


<style scoped>
.read-the-docs {
  color: #888;
}
</style>
