<template>
  <h1>{{ msg }}</h1>

  <div class="card">
    <button type="button" @click="count++">count is {{ count }}</button>
  </div>
  <n-space vertical>
    <!-- <n-card title="Automata Import Teszt"> -->
      <n-button type="success" @click="checkSystemHealth">Ez működik!</n-button>
    <!-- </n-card> -->
  </n-space>

</template>


<script setup>
import { ref, onMounted } from 'vue'
import { getBackendIsAlive, systemIsHealthy } from '@/api/health';

defineProps({
  msg: String,

})

const count = ref(0)

onMounted(async() => {
  const isAlive = await getBackendIsAlive();
  console.log("Backend is alive:", isAlive);
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
