import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar.jsx";
import Footer from "./components/Footer.jsx";
import { ProtectedRoute } from "./components/UI.jsx";

import Home from "./pages/Home.jsx";
import Planner from "./pages/Planner.jsx";
import Destination from "./pages/Destination.jsx";
import Transportation from "./pages/Transportation.jsx";
import MapPage from "./pages/MapPage.jsx";
import Hotels from "./pages/Hotels.jsx";
import Restaurants from "./pages/Restaurants.jsx";
import Weather from "./pages/Weather.jsx";
import Budget from "./pages/Budget.jsx";
import Itinerary from "./pages/Itinerary.jsx";
import SavedTrips from "./pages/SavedTrips.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Profile from "./pages/Profile.jsx";
import NotFound from "./pages/NotFound.jsx";

export default function App() {
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem("dayplan_theme") === "dark");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("dayplan_theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/planner" element={<Planner />} />
          <Route path="/destination" element={<Destination />} />
          <Route path="/transportation" element={<Transportation />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/hotels" element={<Hotels />} />
          <Route path="/restaurants" element={<Restaurants />} />
          <Route path="/weather" element={<Weather />} />
          <Route path="/budget" element={<Budget />} />
          <Route path="/itinerary" element={<Itinerary />} />
          <Route
            path="/saved-trips"
            element={
              <ProtectedRoute>
                <SavedTrips />
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
