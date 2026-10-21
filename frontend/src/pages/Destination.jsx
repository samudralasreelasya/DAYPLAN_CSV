import { motion } from "framer-motion";
import { FiMapPin, FiSun } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

export default function Destination() {
  const { tripData } = useTrip();

  if (!tripData) return <EmptyTripState />;

  const { destination, attractions, weather } = tripData;

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          eyebrow="Destination"
          title={destination?.displayName?.split(",").slice(0, 2).join(", ") || destination?.name}
          subtitle={`Lat ${destination?.lat?.toFixed(2)}, Lon ${destination?.lon?.toFixed(2)}`}
        />

        <Card className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm">
            <FiSun className="text-accent-500" />
            <span>Best time to visit: <strong>{tripData.destination && weather ? "See Weather tab" : "N/A"}</strong></span>
          </div>
        </Card>

        <h3 className="mb-4 text-xl font-semibold">Tourist Attractions</h3>
        {attractions?.length ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {attractions.map((a, i) => (
              <Card key={i}>
                <motion.img
                  src={`https://source.unsplash.com/400x260/?travel,landmark,${encodeURIComponent(a.name)}`}
                  alt={a.name}
                  className="mb-3 h-40 w-full rounded-xl object-cover"
                  onError={(e) => (e.target.style.display = "none")}
                />
                <div className="flex items-start justify-between">
                  <h4 className="font-semibold">{a.name}</h4>
                </div>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{a.category}</p>
                <p className="mt-2 flex items-center gap-1 text-xs text-slate-400">
                  <FiMapPin /> {a.distanceKm != null ? `${a.distanceKm} km away` : "Distance unavailable"}
                </p>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">No attractions found nearby for this destination.</p>
        )}
      </div>
    </section>
  );
}