import { useEffect, useState } from "react";
import { FiTrash2, FiMapPin, FiUsers, FiCalendar } from "react-icons/fi";
import { savedApi } from "../api/api.js";
import { Card, SectionHeading, Loader, ErrorBanner } from "../components/UI.jsx";

export default function SavedTrips() {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const res = await savedApi.listTrips();
      setTrips(res.data);
    } catch (err) {
      setError(err.response?.data?.error || "Could not load saved trips.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id) => {
    try {
      await savedApi.deleteTrip(id);
      setTrips((prev) => prev.filter((t) => t.id !== id));
    } catch {
      setError("Could not delete trip.");
    }
  };

  if (loading) return <Loader label="Loading your saved trips..." />;

  return (
    <section className="mx-auto max-w-5xl px-5 py-16">
      <SectionHeading eyebrow="Your Trips" title="Saved Trips" subtitle="Revisit itineraries you've saved for later." />

      {error && <div className="mb-6"><ErrorBanner message={error} /></div>}

      {trips.length === 0 ? (
        <p className="text-center text-slate-500">You haven't saved any trips yet. Plan one to get started!</p>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {trips.map((t) => (
            <Card key={t.id}>
              <div className="flex items-start justify-between">
                <h4 className="flex items-center gap-2 font-semibold">
                  <FiMapPin className="text-primary-500" /> {t.origin} → {t.destination}
                </h4>
                <button onClick={() => handleDelete(t.id)} className="text-slate-400 hover:text-red-500" aria-label="Delete trip">
                  <FiTrash2 />
                </button>
              </div>
              <div className="mt-3 flex gap-4 text-sm text-slate-500 dark:text-slate-400">
                <span className="flex items-center gap-1"><FiUsers /> {t.people}</span>
                <span className="flex items-center gap-1"><FiCalendar /> {t.days} days</span>
              </div>
              <p className="mt-2 text-xs text-slate-400">Saved on {new Date(t.createdAt).toLocaleDateString()}</p>
            </Card>
          ))}
        </div>
      )}
    </section>
  );
}
