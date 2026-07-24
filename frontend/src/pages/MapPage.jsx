import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import { useEffect } from "react";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

// Fix default marker icon paths (Leaflet + Vite bundling quirk)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function FitBounds({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length) map.fitBounds(positions, { padding: [40, 40] });
  }, [positions, map]);
  return null;
}

export default function MapPage() {
  const { tripData } = useTrip();
  if (!tripData) return <EmptyTripState />;

  const { origin, destination, route } = tripData;
  const originPos = [origin.lat, origin.lon];
  const destPos = [destination.lat, destination.lon];

  const routeCoords =
    route?.geometry?.coordinates?.map(([lon, lat]) => [lat, lon]) || [originPos, destPos];

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-6xl">
        <SectionHeading eyebrow="Route" title="Map & Directions" subtitle={`${route?.distanceKm} km · ~${Math.round(route?.durationMinutes / 60)}h ${route?.durationMinutes % 60}m driving`} />

        <Card className="!p-2">
          <div style={{ height: "500px" }}>
            <MapContainer center={originPos} zoom={6} scrollWheelZoom={true}>
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={originPos}>
                <Popup>Origin: {origin.name}</Popup>
              </Marker>
              <Marker position={destPos}>
                <Popup>Destination: {destination.name}</Popup>
              </Marker>
              <Polyline positions={routeCoords} pathOptions={{ color: "#2563eb", weight: 4 }} />
              <FitBounds positions={routeCoords} />
            </MapContainer>
          </div>
        </Card>

        <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
          <Card>
            <p className="text-sm text-slate-500">Distance</p>
            <p className="text-2xl font-bold">{route?.distanceKm} km</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">Driving Time</p>
            <p className="text-2xl font-bold">
              {Math.round(route?.durationMinutes / 60)}h {route?.durationMinutes % 60}m
            </p>
          </Card>
        </div>
      </div>
    </section>
  );
}
