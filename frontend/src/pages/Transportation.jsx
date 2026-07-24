import { FiTruck, FiAlertCircle } from "react-icons/fi";
import { FaPlane, FaTrain, FaBus, FaCar } from "react-icons/fa";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

const ICONS = { flight: <FaPlane />, train: <FaTrain />, bus: <FaBus />, car: <FaCar /> };

export default function Transportation() {
  const { tripData } = useTrip();
  if (!tripData) return <EmptyTripState />;

  const { route } = tripData;
  // Derive transport options client-side from the route we already have,
  // matching the heuristic used by /api/transport.
  const distanceKm = route?.distanceKm || 0;
  const options = [
    { mode: "car", available: true, durationMinutes: route?.durationMinutes, cost: (distanceKm * 0.1).toFixed(0) },
    { mode: "bus", available: distanceKm <= 1200, durationMinutes: Math.round((distanceKm / 55) * 60), cost: (distanceKm * 0.05).toFixed(0) },
    { mode: "train", available: distanceKm <= 2000, durationMinutes: Math.round((distanceKm / 80) * 60), cost: (distanceKm * 0.07).toFixed(0) },
    { mode: "flight", available: distanceKm >= 300, durationMinutes: Math.round((distanceKm / 700) * 60 + 90), cost: (distanceKm * 0.15).toFixed(0) },
  ];

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-6xl">
        <SectionHeading eyebrow="Transportation" title="Getting There" subtitle={`Distance: ${distanceKm} km`} />

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {options.map((o) => (
            <Card key={o.mode} className={`text-center ${!o.available && "opacity-50"}`}>
              <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-primary-100 text-2xl text-primary-600 dark:bg-primary-900/40">
                {ICONS[o.mode]}
              </div>
              <h4 className="font-semibold capitalize">{o.mode}</h4>
              {o.available ? (
                <>
                  <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    ~{Math.round(o.durationMinutes / 60)}h {o.durationMinutes % 60}m
                  </p>
                  <p className="text-xs text-slate-400">Est. ${o.cost}</p>
                </>
              ) : (
                <p className="mt-2 text-sm text-slate-400">Not available</p>
              )}
            </Card>
          ))}
        </div>

        <div className="mt-8 flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
          <FiAlertCircle /> Travel durations and costs are estimates. Verify with a live booking provider before purchasing.
        </div>
      </div>
    </section>
  );
}
