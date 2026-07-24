import { Link } from "react-router-dom";
import { FiInstagram, FiTwitter, FiFacebook } from "react-icons/fi";

export default function Footer() {
  return (
    <footer className="mt-20 border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-10 px-5 py-12 md:grid-cols-4">
        <div>
          <h3 className="font-display text-xl font-extrabold text-primary-600">
            Day<span className="text-accent-500">Plan</span>
          </h3>
          <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
            Plan smarter. Travel better. AI-assisted trip planning powered by open data.
          </p>
          <div className="mt-4 flex gap-3 text-slate-400">
            <FiInstagram /> <FiTwitter /> <FiFacebook />
          </div>
        </div>

        <div>
          <h4 className="mb-3 font-semibold">Explore</h4>
          <ul className="space-y-2 text-sm text-slate-500 dark:text-slate-400">
            <li><Link to="/planner">Plan a Trip</Link></li>
            <li><Link to="/saved-trips">Saved Trips</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="mb-3 font-semibold">Company</h4>
          <ul className="space-y-2 text-sm text-slate-500 dark:text-slate-400">
            <li>About</li>
            <li>Contact</li>
            <li>Careers</li>
          </ul>
        </div>

        <div>
          <h4 className="mb-3 font-semibold">Legal</h4>
          <ul className="space-y-2 text-sm text-slate-500 dark:text-slate-400">
            <li>Privacy Policy</li>
            <li>Terms of Service</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-slate-200 py-5 text-center text-xs text-slate-400 dark:border-slate-800">
        © {new Date().getFullYear()} DayPlan. Built with free open data — OpenStreetMap, OSRM, Open-Meteo, Overpass.
      </div>
    </footer>
  );
}
