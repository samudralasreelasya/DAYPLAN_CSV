// A small colored-dot badge for restaurant veg status, following the
// classic Indian menu convention: green square/dot = veg, red = non-veg.
// "both" gets a half-and-half treatment since that's a real, common case
// (a restaurant serving both) rather than an edge case to hide.
// "NA" (no diet tag in OSM, or genuinely unknown) renders nothing rather
// than a misleading badge - silence is more honest than a guess here.

const STATUS_CONFIG = {
  veg: { label: "Veg", dot: "bg-emerald-500", text: "text-emerald-700 dark:text-emerald-400" },
  "non-veg": { label: "Non-Veg", dot: "bg-red-500", text: "text-red-700 dark:text-red-400" },
  both: { label: "Veg & Non-Veg", dot: "bg-gradient-to-r from-emerald-500 to-red-500", text: "text-slate-600 dark:text-slate-300" },
};

export default function VegBadge({ vegStatus }) {
  const config = STATUS_CONFIG[vegStatus];
  if (!config) return null; // vegStatus is "NA" or missing - say nothing rather than guess

  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${config.text}`}>
      <span className={`h-2.5 w-2.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  );
}
