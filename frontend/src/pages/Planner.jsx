import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { FiMapPin, FiUsers, FiCalendar, FiDollarSign, FiSearch } from "react-icons/fi";
import { tripApi } from "../api/api.js";
import { useTrip } from "../context/TripContext.jsx";
import { ErrorBanner } from "../components/UI.jsx";

const PREFERENCES = [
  { value: "budget", label: "Budget" },
  { value: "standard", label: "Standard" },
  { value: "luxury", label: "Luxury" },
];

export default function Planner() {
  const { searchForm, setSearchForm, setTripData } = useTrip();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSearchForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!searchForm.origin || !searchForm.destination) {
      setError("Please enter both a starting location and a destination.");
      return;
    }
    setLoading(true);
    try {
      const res = await tripApi.planTrip(searchForm);
      setTripData(res.data);
      navigate("/destination");
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong while planning your trip.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mx-auto max-w-3xl px-5 py-16">
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="section-title text-center">Plan Your Trip</h1>
        <p className="mt-2 text-center text-slate-500 dark:text-slate-400">
          Tell us where you're headed and we'll handle the rest.
        </p>
      </motion.div>

      <form onSubmit={handleSubmit} className="glass-card mt-10 space-y-5 p-8">
        {error && <ErrorBanner message={error} />}

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <Field icon={<FiMapPin />} label="Current Location">
            <input
              name="origin"
              value={searchForm.origin}
              onChange={handleChange}
              placeholder="e.g. Mumbai"
              className="input-field"
              required
            />
          </Field>
          <Field icon={<FiMapPin />} label="Destination">
            <input
              name="destination"
              value={searchForm.destination}
              onChange={handleChange}
              placeholder="e.g. Goa"
              className="input-field"
              required
            />
          </Field>
          <Field icon={<FiUsers />} label="Number of People">
            <input
              type="number"
              min="1"
              name="people"
              value={searchForm.people}
              onChange={handleChange}
              className="input-field"
            />
          </Field>
          <Field icon={<FiCalendar />} label="Number of Days">
            <input
              type="number"
              min="1"
              name="days"
              value={searchForm.days}
              onChange={handleChange}
              className="input-field"
            />
          </Field>
          <Field icon={<FiDollarSign />} label="Budget (USD)">
            <input
              type="number"
              min="0"
              name="budget"
              value={searchForm.budget}
              onChange={handleChange}
              className="input-field"
            />
          </Field>
          <Field icon={<FiSearch />} label="Travel Preference">
            <select name="preference" value={searchForm.preference} onChange={handleChange} className="input-field">
              {PREFERENCES.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </Field>
        </div>

        <button type="submit" disabled={loading} className="btn-primary w-full justify-center text-lg disabled:opacity-60">
          {loading ? "Planning your trip..." : "Search"}
        </button>
      </form>
    </section>
  );
}

function Field({ icon, label, children }) {
  return (
    <label className="block">
      <span className="mb-1 flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300">
        {icon} {label}
      </span>
      {children}
    </label>
  );
}
