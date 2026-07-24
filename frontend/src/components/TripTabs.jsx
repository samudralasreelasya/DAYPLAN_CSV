import { NavLink } from "react-router-dom";

const TABS = [
  { to: "/destination", label: "Destination" },
  { to: "/transportation", label: "Transport" },
  { to: "/map", label: "Map" },
  { to: "/hotels", label: "Hotels" },
  { to: "/restaurants", label: "Restaurants" },
  { to: "/weather", label: "Weather" },
  { to: "/budget", label: "Budget" },
  { to: "/itinerary", label: "Itinerary" },
];

export default function TripTabs() {
  return (
    <div className="sticky top-[65px] z-40 -mx-5 mb-8 overflow-x-auto border-b border-slate-200 bg-white/90 px-5 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
      <div className="mx-auto flex max-w-6xl gap-2">
        {TABS.map((t) => (
          <NavLink
            key={t.to}
            to={t.to}
            className={({ isActive }) =>
              `whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-primary-600 text-white"
                  : "text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
              }`
            }
          >
            {t.label}
          </NavLink>
        ))}
      </div>
    </div>
  );
}
