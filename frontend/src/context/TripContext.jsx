import { createContext, useContext, useState } from "react";

// Holds the last full trip-plan result so every page (Destination, Transport,
// Map, Hotels, Restaurants, Weather, Budget, Itinerary) can read it without
// re-fetching or re-passing props through routes.
const TripContext = createContext(null);

export function TripProvider({ children }) {
  const [tripData, setTripData] = useState(null);
  const [searchForm, setSearchForm] = useState({
    origin: "",
    destination: "",
    people: 2,
    days: 3,
    budget: 500,
    preference: "standard",
  });

  return (
    <TripContext.Provider value={{ tripData, setTripData, searchForm, setSearchForm }}>
      {children}
    </TripContext.Provider>
  );
}

export const useTrip = () => useContext(TripContext);
