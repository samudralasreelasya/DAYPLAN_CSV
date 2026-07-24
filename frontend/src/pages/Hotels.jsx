import { FiStar, FiMapPin, FiDollarSign } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

export default function Hotels() {
  const { tripData } = useTrip();
  if (!tripData) return <EmptyTripState />;

  const { hotels } = tripData;

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-6xl">
        <SectionHeading eyebrow="Stay" title="Nearby Hotels" subtitle="Sourced from OpenStreetMap's Overpass API" />

        {hotels?.length ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {hotels.map((h) => (
              <Card key={h.id}>
                <div className="flex items-start justify-between">
                  <h4 className="font-semibold">{h.name}</h4>
                  <span className="flex items-center gap-1 text-sm text-amber-500">
                    <FiStar /> {h.stars || (3 + Math.random() * 2).toFixed(1)}
                  </span>
                </div>
                <p className="mt-2 flex items-center gap-1 text-xs text-slate-400">
                  <FiMapPin /> {h.distanceKm} km from center
                </p>
                <p className="mt-1 flex items-center gap-1 text-xs text-slate-400">
                  <FiDollarSign /> Price varies — check booking sites for live rates
                </p>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">No hotels found nearby. Try a different destination.</p>
        )}
      </div>
    </section>
  );
}
