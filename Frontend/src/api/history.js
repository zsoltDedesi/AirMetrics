import { apiClient } from './client'

export const getHistory = async (since) => {
  const response = await apiClient.get('/history', {
    params: { since },
  })

  return response.data
}
