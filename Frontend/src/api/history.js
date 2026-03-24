import { apiClient } from "./client";

export const getHistory = async (timeInterval) => {
  const response = await apiClient.get("/history", {
    params: {
      since: timeInterval,
    },
  });

  return response.data;
};
