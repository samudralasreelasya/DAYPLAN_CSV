import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token to every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("dayplan_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  register: (payload) => api.post("/api/register", payload),
  login: (payload) => api.post("/api/login", payload),
  profile: () => api.get("/api/profile"),
};

export const tripApi = {
  planTrip: (payload) => api.post("/api/plan-trip", payload),
  getDestination: (name) => api.get("/api/destination", { params: { name } }),
  getTransport: (origin, destination) =>
    api.get("/api/transport", { params: { origin, destination } }),
  getRoute: (origin, destination) =>
    api.get("/api/route", { params: { origin, destination } }),
  getHotels: (destination) => api.get("/api/hotels", { params: { destination } }),
  getRestaurants: (destination) => api.get("/api/restaurants", { params: { destination } }),
  getWeather: (destination) => api.get("/api/weather", { params: { destination } }),
  calculateBudget: (payload) => api.post("/api/budget", payload),
  generateItinerary: (payload) => api.post("/api/itinerary", payload),
};

export const savedApi = {
  saveTrip: (payload) => api.post("/api/trips", payload),
  listTrips: () => api.get("/api/trips"),
  deleteTrip: (id) => api.delete(`/api/trips/${id}`),
  addFavorite: (payload) => api.post("/api/favorites", payload),
  listFavorites: () => api.get("/api/favorites"),
  deleteFavorite: (id) => api.delete(`/api/favorites/${id}`),
};

export default api;
