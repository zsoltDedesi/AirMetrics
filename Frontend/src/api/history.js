import { apiClient } from "./client";

// Fetch historical sensor data based on a specified time interval (e.g., last 24 hours)
export const getHistory = async (timeInterval) => {
  const response = await apiClient.get("/history", {
    params: {
      since: timeInterval,
    },
  });

  return response.data;
};
