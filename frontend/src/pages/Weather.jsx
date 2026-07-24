import { FiDroplet, FiWind, FiCloudRain } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

export default function Weather() {
  const { tripData } = useTrip();
  if (!tripData) return <EmptyTripState />;

  const { weather, destination } = tripData;
  const { current, forecast } = weather || {};

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-6xl">
        <SectionHeading eyebrow="Weather" title={`Weather in ${destination?.name}`} subtitle="Live data from Open-Meteo" />

        <Card className="mb-8 flex flex-wrap items-center justify-around gap-6 text-center">
          <div>
            <p className="text-4xl font-bold">{Math.round(current?.temperature)}°C</p>
            <p className="text-sm text-slate-500">{current?.condition}</p>
          </div>
          <div className="flex items-center gap-2">
            <FiDroplet className="text-primary-500" />
            <div>
              <p className="font-semibold">{current?.humidity}%</p>
              <p className="text-xs text-slate-400">Humidity</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <FiWind className="text-primary-500" />
            <div>
              <p className="font-semibold">{current?.windSpeed} km/h</p>
              <p className="text-xs text-slate-400">Wind</p>
            </div>
          </div>
        </Card>

        <h3 className="mb-4 text-xl font-semibold">5-Day Forecast</h3>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {forecast?.map((f) => (
            <Card key={f.date} className="text-center">
              <p className="text-sm font-semibold">{new Date(f.date).toLocaleDateString(undefined, { weekday: "short" })}</p>
              <p className="mt-2 text-lg font-bold">{Math.round(f.maxTemp)}°</p>
              <p className="text-xs text-slate-400">{Math.round(f.minTemp)}° min</p>
              <p className="mt-2 flex items-center justify-center gap-1 text-xs text-primary-500">
                <FiCloudRain /> {f.rainChance}%
              </p>
              <p className="mt-1 text-[11px] text-slate-400">{f.condition}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
