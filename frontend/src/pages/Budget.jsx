import { FiTruck, FiHome, FiCoffee, FiNavigation, FiTag } from "react-icons/fi";
import { useTrip } from "../context/TripContext.jsx";
import TripTabs from "../components/TripTabs.jsx";
import EmptyTripState from "../components/EmptyTripState.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

const ROWS = [
  { key: "travelCost", label: "Travel Cost", icon: <FiTruck /> },
  { key: "hotelCost", label: "Hotel Cost", icon: <FiHome /> },
  { key: "foodCost", label: "Food Cost", icon: <FiCoffee /> },
  { key: "localTransport", label: "Local Transport", icon: <FiNavigation /> },
  { key: "entryFees", label: "Entry Fees", icon: <FiTag /> },
];

export default function Budget() {
  const { tripData } = useTrip();
  if (!tripData) return <EmptyTripState />;

  const { budget, userBudget } = tripData;
  const over = userBudget && budget?.totalEstimatedBudget > userBudget;

  return (
    <section className="px-5 pb-16">
      <TripTabs />
      <div className="mx-auto max-w-3xl">
        <SectionHeading eyebrow="Budget" title="Estimated Budget Summary" subtitle={budget?.note} />

        <Card>
          <div className="divide-y divide-slate-200 dark:divide-slate-700">
            {ROWS.map((r) => (
              <div key={r.key} className="flex items-center justify-between py-3">
                <span className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                  {r.icon} {r.label}
                </span>
                <span className="font-semibold">${budget?.[r.key]?.toFixed(2)}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between rounded-xl bg-primary-50 px-4 py-4 dark:bg-primary-900/30">
            <span className="text-lg font-bold">Total Estimated Budget</span>
            <span className="text-2xl font-extrabold text-primary-600">
              ${budget?.totalEstimatedBudget?.toFixed(2)}
            </span>
          </div>
          {userBudget > 0 && (
            <p className={`mt-3 text-sm ${over ? "text-red-500" : "text-green-600"}`}>
              {over
                ? `This exceeds your stated budget of $${userBudget} by $${(budget.totalEstimatedBudget - userBudget).toFixed(2)}.`
                : `You're within your stated budget of $${userBudget}.`}
            </p>
          )}
        </Card>
      </div>
    </section>
  );
}
