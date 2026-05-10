import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: BASE_URL });

// Attach JWT token to every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const sendQuery = (query) =>
  api.post("/api/query", { query }).then((r) => r.data);

export const adminLogin = (password) =>
  api.post("/api/admin/login", { password }).then((r) => r.data);

export const getStats = () =>
  api.get("/api/admin/stats").then((r) => r.data);

// PDFs
export const uploadPDF = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/api/admin/upload-pdf", form).then((r) => r.data);
};
export const listPDFs = () =>
  api.get("/api/admin/pdfs").then((r) => r.data);
export const deletePDF = (filename) =>
  api.delete(`/api/admin/pdf/${encodeURIComponent(filename)}`).then((r) => r.data);

// Excel
export const uploadExcel = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/api/admin/upload-excel", form).then((r) => r.data);
};
export const listExcels = () =>
  api.get("/api/admin/excels").then((r) => r.data);
export const deleteExcel = (filename) =>
  api.delete(`/api/admin/excel/${encodeURIComponent(filename)}`).then((r) => r.data);

// Websites
export const indexWebsite = (url, include_pdfs = true) =>
  api.post("/api/admin/index-website", { url, include_pdfs }).then((r) => r.data);
export const listWebsites = () =>
  api.get("/api/admin/websites").then((r) => r.data);
export const deleteWebsite = (url) =>
  api.delete("/api/admin/website", { params: { url } }).then((r) => r.data);

export const clearCollection = (name) =>
  api.delete(`/api/admin/clear/${name}`).then((r) => r.data);
