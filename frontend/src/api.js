import axios from "axios";

const API_BASE = "";

export const predictChurn = async (customerData) => {
  const response = await axios.post(`${API_BASE}/predict`, customerData);
  return response.data;
};

export const getModelInfo = async () => {
  const response = await axios.get(`${API_BASE}/model-info`);
  return response.data;
};
