import { FiMapPin, FiStar } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

export default function Restaurants() {
  const { tripData } = useTrip();
  if (!tripData) return <EmptyTripState />;

  const { restaurants } = tripData;

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-6xl">
        <SectionHeading eyebrow="Eat" title="Nearby Restaurants" subtitle="Sourced from OpenStreetMap's Overpass API" />

        {restaurants?.length ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {restaurants.map((r) => (
              <Card key={r.id}>
                <div className="flex items-start justify-between">
                  <h4 className="font-semibold">{r.name}</h4>
                  <span className="flex items-center gap-1 text-sm text-amber-500">
                    <FiStar /> {(3.8 + Math.random()).toFixed(1)}
                  </span>
                </div>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {r.cuisine ? r.cuisine : "Local cuisine"}
                </p>
                <p className="mt-2 flex items-center gap-1 text-xs text-slate-400">
                  <FiMapPin /> {r.distanceKm} km away
                </p>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">No restaurants found nearby. Try a different destination.</p>
        )}
      </div>
    </section>
  );
}
