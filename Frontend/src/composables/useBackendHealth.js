import { ref } from 'vue'

import { getBackendIsAlive, systemIsHealthy } from '@/api/health'

export function useBackendHealth() {
  const isAlive = ref(false)
  const readiness = ref(null)
  const isChecking = ref(false)
  const error = ref(null)

  const checkLiveness = async () => {
    try {
      const response = await getBackendIsAlive()
      isAlive.value = Boolean(response.ok)
      error.value = null
      return response
    } catch (healthError) {
      isAlive.value = false
      error.value = healthError
      throw healthError
    }
  }

  const checkReadiness = async () => {
    isChecking.value = true

    try {
      const response = await systemIsHealthy()
      readiness.value = response
      error.value = null
      return response
    } catch (healthError) {
      error.value = healthError
      throw healthError
    } finally {
      isChecking.value = false
    }
  }

  return {
    isAlive,
    readiness,
    isChecking,
    error,
    checkLiveness,
    checkReadiness,
  }
}
