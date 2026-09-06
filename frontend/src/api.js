import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export const getStats = () => api.get("/stats").then((res) => res.data);
export const getFraudByType = () =>
  api.get("/fraud-by-type").then((res) => res.data);
export const getFraudOverTime = () =>
  api.get("/fraud-over-time").then((res) => res.data);
export const getModelInfo = () =>
  api.get("/model-info").then((res) => res.data);
export const predict = (transaction) =>
  api.post("/predict", transaction).then((res) => res.data);
