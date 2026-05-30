import { onBeforeUnmount, ref } from 'vue'

const SENSOR_NAMES = {
  DS18B20: 'ds18b20',
  AM2302: 'am2302',
}

function createInitialReadings() {
  return {
    [SENSOR_NAMES.DS18B20]: null,
    [SENSOR_NAMES.AM2302]: null,
  }
}

export function useSensorStream() {
  const readings = ref(createInitialReadings())
  const isConnected = ref(false)
  const error = ref(null)

  let eventSource = null

  const connect = () => {
    if (eventSource) {
      return
    }

    eventSource = new EventSource(`${import.meta.env.VITE_API_BASE_BACKEND_URL}/stream`)

    eventSource.addEventListener('open', () => {
      isConnected.value = true
      error.value = null
    })

    eventSource.addEventListener('reading', (event) => {
      try {
        const reading = JSON.parse(event.data)
        if (reading.sensor in readings.value) {
          readings.value = {
            ...readings.value,
            [reading.sensor]: reading,
          }
        }
      } catch (parseError) {
        error.value = parseError
      }
    })

    eventSource.onerror = (streamError) => {
      isConnected.value = false
      error.value = streamError
    }
  }

  const disconnect = () => {
    if (!eventSource) {
      return
    }

    eventSource.close()
    eventSource = null
    isConnected.value = false
  }

  onBeforeUnmount(disconnect)

  return {
    readings,
    isConnected,
    error,
    connect,
    disconnect,
  }
}
