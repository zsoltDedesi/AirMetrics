import { apiClient } from "./client";

export const getBackendIsAlive = async () => {
    const response = await apiClient.get("/health/live");
    return response.data;
  }

export const systemIsHealthy = async () => {
    const response = await apiClient.get("/health/ready");
    return response.data;
  }


// export default {