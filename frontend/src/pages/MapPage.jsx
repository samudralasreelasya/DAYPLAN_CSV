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

// A numbered round badge, so marker 3 on the map is "3" in the On the Way list.
function stopIcon(number) {
  return L.divIcon({
    className: "",
    html: `<div style="width:26px;height:26px;border-radius:50%;background:#16a34a;color:#fff;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);display:flex;align-items:center;justify-content:center;font:600 12px sans-serif;">${number}</div>`,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
    popupAnchor: [0, -13],
  });
}

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

  const { origin, destination, route, routeHighlights } = tripData;
  const stops = Array.isArray(routeHighlights) ? routeHighlights : [];
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
              {stops.map((stop, i) => (
                <Marker key={`${stop.name}-${i}`} position={[stop.lat, stop.lon]} icon={stopIcon(i + 1)}>
                  <Popup>
                    <strong>{stop.name}</strong>
                    <br />
                    {stop.alongKm} km from start
                    {stop.offRouteKm >= 1 ? ` · ${stop.offRouteKm} km off the road` : ""}
                    {Array.isArray(stop.tags) && stop.tags.length > 0 && (
                      <>
                        <br />
                        {stop.tags.slice(0, 3).join(", ")}
                      </>
                    )}
                  </Popup>
                </Marker>
              ))}
              <FitBounds positions={routeCoords} />
            </MapContainer>
          </div>
        </Card>

        {stops.length > 0 && (
          <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
            Numbered green markers are stops along your route, in travel order. Click one for details,
            or see the full list on the On the Way tab.
          </p>
        )}

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