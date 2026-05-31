import { apiClient } from './client'

export const getSystemStatus = async () => {
  const response = await apiClient.get('/system/status')
  return response.data
}
