import { Link } from "react-router-dom";
import { FiMapPin } from "react-icons/fi";

export default function EmptyTripState() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center px-5 py-24 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary-100 text-3xl text-primary-600 dark:bg-primary-900/40">
        <FiMapPin />
      </div>
      <h2 className="text-xl font-semibold">No trip planned yet</h2>
      <p className="mt-2 text-slate-500 dark:text-slate-400">
        Start by searching for a destination on the Planner page.
      </p>
      <Link to="/planner" className="btn-primary mt-6">
        Plan My Trip
      </Link>
    </div>
  );
}
