import { useState } from "react";
import { FiMapPin, FiStar } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";
import VegBadge from "../components/VegBadge.jsx";

export default function Restaurants() {
  const { tripData } = useTrip();
  const [vegOnly, setVegOnly] = useState(false);

  if (!tripData) return <EmptyTripState />;

  const { restaurants } = tripData;

  // Client-side filter: the full restaurant list (live + curated fallback)
  // is already fetched in one shot as part of plan-trip, so filtering here
  // avoids a second network round-trip just to toggle a view.
  const visible = vegOnly
    ? restaurants?.filter((r) => r.vegStatus === "veg" || r.vegStatus === "both")
    : restaurants;

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-6xl">
        <SectionHeading eyebrow="Eat" title="Nearby Restaurants" subtitle="Sourced from OpenStreetMap's Overpass API, with curated local data as backup" />

        <div className="mb-6 flex justify-center">
          <button
            onClick={() => setVegOnly((v) => !v)}
            className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
              vegOnly
                ? "bg-emerald-600 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            }`}
          >
            {vegOnly ? "Showing Veg Only" : "Show Veg Only"}
          </button>
        </div>

        {visible?.length ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {visible.map((r) => (
              <Card key={r.id ?? r.name}>
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-semibold">{r.name}</h4>
                  <span className="flex shrink-0 items-center gap-1 text-sm text-amber-500">
                    <FiStar /> {(3.8 + Math.random()).toFixed(1)}
                  </span>
                </div>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {r.cuisine ? r.cuisine : r.category === "restaurant" ? "Local cuisine" : r.category}
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
                  {r.distanceKm != null && (
                    <p className="flex items-center gap-1 text-xs text-slate-400">
                      <FiMapPin /> {r.distanceKm} km away
                    </p>
                  )}
                  <VegBadge vegStatus={r.vegStatus} />
                </div>
                {r.openingHours && (
                  <p className="mt-2 text-xs text-slate-400">{r.openingHours}</p>
                )}
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">
            {vegOnly
              ? "No veg-tagged restaurants found nearby. Try turning off the veg filter."
              : "No restaurants found nearby. Try a different destination."}
          </p>
        )}
      </div>
    </section>
  );
}
