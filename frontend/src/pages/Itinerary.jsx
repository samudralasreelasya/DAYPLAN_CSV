import { useState } from "react";
import { FiPackage, FiCheckCircle, FiDownload, FiSave } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { savedApi } from "../api/api.js";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading, ErrorBanner } from "../components/UI.jsx";

export default function Itinerary() {
  const { tripData, searchForm } = useTrip();
  const { user } = useAuth();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  if (!tripData) return <EmptyTripState />;

  const { itinerary, packingSuggestions, destination, origin } = tripData;

  const handleSave = async () => {
    if (!user) {
      setError("Please log in to save this trip.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await savedApi.saveTrip({
        origin: origin?.name,
        destination: destination?.name,
        people: searchForm.people,
        days: searchForm.days,
        budget: searchForm.budget,
        preference: searchForm.preference,
        itinerary,
        budgetBreakdown: tripData.budget,
      });
      setSaved(true);
    } catch (err) {
      setError(err.response?.data?.error || "Could not save trip.");
    } finally {
      setSaving(false);
    }
  };

  const handleDownload = () => {
    const text = itinerary
      .map((d) => `${d.title}\n${d.activities.map((a) => `  - ${a}`).join("\n")}\n`)
      .join("\n");
    const blob = new Blob([`DayPlan Itinerary: ${destination?.name}\n\n${text}`], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `dayplan-itinerary-${destination?.name}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-4xl">
        <SectionHeading eyebrow="AI Itinerary" title={`Your Trip to ${destination?.name}`} subtitle="Generated from real nearby attractions and forecasted weather" />

        {error && <div className="mb-6"><ErrorBanner message={error} /></div>}

        <div className="mb-6 flex flex-wrap gap-3">
          <button onClick={handleSave} disabled={saving || saved} className="btn-primary text-sm disabled:opacity-60">
            <FiSave /> {saved ? "Trip Saved" : saving ? "Saving..." : "Save Trip"}
          </button>
          <button onClick={handleDownload} className="btn-secondary text-sm">
            <FiDownload /> Download Itinerary
          </button>
        </div>

        <div className="space-y-6">
          {itinerary?.map((day) => (
            <Card key={day.day}>
              <h3 className="text-lg font-bold">{day.title}</h3>
              {day.weather && <p className="mt-1 text-xs text-primary-500">{day.weather}</p>}
              <ul className="mt-3 space-y-2">
                {day.activities.map((act, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-300">
                    <FiCheckCircle className="mt-0.5 shrink-0 text-primary-500" /> {act}
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>

        <Card className="mt-8">
          <h3 className="mb-3 flex items-center gap-2 text-lg font-bold">
            <FiPackage /> Packing Suggestions
          </h3>
          <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {packingSuggestions?.map((p, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                <FiCheckCircle className="text-accent-500" /> {p}
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </section>
  );
}
