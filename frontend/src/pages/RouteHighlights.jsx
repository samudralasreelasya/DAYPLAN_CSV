import { FiMapPin, FiNavigation } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

export default function RouteHighlights() {
  const { tripData } = useTrip();

  if (!tripData) return <EmptyTripState />;

  // Already fetched as part of /api/plan-trip, so no extra network call here.
  // The list arrives in travel order (nearest the start first).
  const { routeHighlights, route, origin, destination } = tripData;
  const stops = Array.isArray(routeHighlights) ? routeHighlights : [];

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-3xl">
        <SectionHeading
          eyebrow="On the way"
          title="Stops Along Your Route"
          subtitle={
            route
              ? `Curated spots within 5 km of the road, ${origin?.name ?? "start"} to ${destination?.name ?? "destination"} (${route.distanceKm} km)`
              : "Curated spots along the driving route"
          }
        />

        {stops.length ? (
          <ol className="relative ml-3 border-l-2 border-primary-200 dark:border-primary-900">
            {stops.map((s, i) => (
              <li key={`${s.name}-${i}`} className="mb-6 ml-6">
                {/* numbered dot sitting on the vertical line */}
                <span className="absolute -left-[13px] flex h-6 w-6 items-center justify-center rounded-full bg-primary-600 text-xs font-semibold text-white">
                  {i + 1}
                </span>
                <Card>
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold">{s.name}</h4>
                    <FiNavigation className="mt-1 shrink-0 text-primary-600" />
                  </div>

                  <p className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <FiMapPin /> {s.alongKm} km from start
                    </span>
                    <span>
                      {s.offRouteKm < 1 ? "right on the road" : `${s.offRouteKm} km off the road`}
                    </span>
                  </p>

                  {Array.isArray(s.tags) && s.tags.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {s.tags.slice(0, 4).map((t) => (
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
              </li>
            ))}
          </ol>
        ) : (
          <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center dark:border-slate-700">
            <p className="font-medium">
              {route ? "No curated stops found along this route." : "No driving route was available for this trip."}
            </p>
            {route && (
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                Our curated data covers 13 cities, so roads that pass through small towns
                may have nothing listed. Check the Highlights tab for spots at your destination.
              </p>
            )}
          </div>
        )}
      </div>
    </section>
  );
}