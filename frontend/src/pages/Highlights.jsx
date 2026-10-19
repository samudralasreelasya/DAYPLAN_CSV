import { FiMapPin, FiCompass } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

export default function Highlights() {
  const { tripData } = useTrip();

  if (!tripData) return <EmptyTripState />;

  // Already fetched as part of /api/plan-trip, so no extra network call here
  // (same approach as Restaurants.jsx).
  const { highlights } = tripData;

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          eyebrow="Explore"
          title="Destination Highlights"
          subtitle="Landmarks, viewpoints and natural spots from OpenStreetMap, with curated local data as backup"
        />

        {highlights?.length ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {highlights.map((h, i) => (
              <Card key={`${h.name}-${i}`}>
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-semibold">{h.name}</h4>
                  <FiCompass className="mt-1 shrink-0 text-primary-600" />
                </div>

                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {h.category === "highlight (curated)" ? "Curated pick" : h.category}
                </p>

                {h.distanceKm != null && (
                  <p className="mt-2 flex items-center gap-1 text-xs text-slate-400">
                    <FiMapPin /> {h.distanceKm} km away
                  </p>
                )}

                {Array.isArray(h.tags) && h.tags.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {h.tags.slice(0, 4).map((t) => (
                      <span
                        key={t}
                        className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">
            No highlights found nearby. Try a different destination.
          </p>
        )}
      </div>
    </section>
  );
}