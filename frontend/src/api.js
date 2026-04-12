import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
  headers: {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
  }
})

export default api;