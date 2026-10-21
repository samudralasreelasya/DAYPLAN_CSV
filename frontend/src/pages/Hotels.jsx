import { FiStar, FiMapPin, FiDollarSign, FiExternalLink } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

export default function Hotels() {
  const { tripData } = useTrip();
  if (!tripData) return <EmptyTripState />;

  const { hotels, hotelsStatus } = tripData;

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          eyebrow="Stay"
          title="Hotels"
          subtitle="OpenStreetMap live data, backed by a curated hotel list"
        />

        {hotelsStatus === "fallback" && (
          <p className="mb-4 text-sm text-slate-500">
            Live hotel data is busy right now, so these come from our curated list instead.
          </p>
        )}

        {hotels?.length ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {hotels.map((h) => (
              <Card key={h.id}>
                <div className="flex items-start justify-between">
                  <h4 className="font-semibold">{h.name}</h4>
                  {h.stars ? (
                    <span className="flex items-center gap-1 text-sm text-amber-500">
                      <FiStar /> {h.stars}
                    </span>
                  ) : null}
                </div>
                {h.category && h.category !== "unclassified" ? (
                  <p className="mt-1 text-xs uppercase tracking-wide text-slate-400">{h.category}</p>
                ) : null}
                <p className="mt-2 flex items-center gap-1 text-xs text-slate-400">
                  <FiMapPin />
                  {h.distanceKm != null ? `${h.distanceKm} km from center` : h.area || "Location not pinned"}
                  {h.distanceKm != null && h.area ? ` - ${h.area}` : ""}
                </p>
                {h.notes ? <p className="mt-2 text-xs text-slate-500">{h.notes}</p> : null}
                <p className="mt-1 flex items-center gap-1 text-xs text-slate-400">
                  <FiDollarSign /> Price varies - check booking sites for live rates
                </p>
                {h.sourceUrl ? (
                  <a
                    href={h.sourceUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-2 inline-flex items-center gap-1 text-xs text-sky-500"
                  >
                    <FiExternalLink /> Source
                  </a>
                ) : null}
              </Card>
            ))}
          </div>
        ) : hotelsStatus === "unavailable" ? (
          <p className="text-slate-500">
            Live hotel data is temporarily unavailable because the OpenStreetMap
            (Overpass) server is busy. Please try again in a few minutes, or check
            a booking site for stays near your destination.
          </p>
        ) : (
          <p className="text-slate-500">No hotels found nearby. Try a different destination.</p>
        )}
      </div>
    </section>
  );
}