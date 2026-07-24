import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { FiMapPin, FiCloud, FiDollarSign, FiCompass } from "react-icons/fi";
import { SectionHeading, Card } from "../components/UI.jsx";

const featured = [
  { name: "Paris, France", img: "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&q=80" },
  { name: "Kyoto, Japan", img: "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&q=80" },
  { name: "Santorini, Greece", img: "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=600&q=80" },
  { name: "Bali, Indonesia", img: "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80" },
];

const whyUs = [
  { icon: <FiMapPin />, title: "Smart Route Planning", desc: "Real driving routes and distances powered by open-source mapping data." },
  { icon: <FiCloud />, title: "Live Weather", desc: "Accurate forecasts so you always know what to pack." },
  { icon: <FiDollarSign />, title: "Budget Estimator", desc: "Transparent cost breakdowns for hotels, food, and transport." },
  { icon: <FiCompass />, title: "AI Itinerary", desc: "Day-wise plans generated from real nearby attractions." },
];

export default function Home() {
  return (
    <div>
      {/* Hero Section — single CTA only */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-accent-400/10 py-24 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
        <div className="mx-auto flex max-w-5xl flex-col items-center px-5 text-center">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="font-display text-5xl font-extrabold tracking-tight md:text-7xl"
          >
            Day<span className="text-primary-600">Plan</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="mt-4 text-xl font-medium text-slate-600 dark:text-slate-300 md:text-2xl"
          >
            Plan Smarter. Travel Better.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-10"
          >
            <Link to="/planner" className="btn-primary text-lg">
              Plan My Trip
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Featured Destinations */}
      <section className="mx-auto max-w-7xl px-5 py-20">
        <SectionHeading eyebrow="Explore" title="Featured Destinations" subtitle="Get inspired by some of the world's most loved places." />
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {featured.map((d) => (
            <Card key={d.name} className="overflow-hidden !p-0">
              <img src={d.img} alt={d.name} className="h-48 w-full object-cover" />
              <div className="p-4">
                <p className="font-semibold">{d.name}</p>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Why Choose DayPlan */}
      <section id="about" className="bg-slate-100/60 py-20 dark:bg-slate-900/40">
        <div className="mx-auto max-w-7xl px-5">
          <SectionHeading eyebrow="Why DayPlan" title="Why Choose DayPlan" subtitle="Everything you need to plan a trip, in one connected flow." />
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {whyUs.map((f) => (
              <Card key={f.title} className="text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary-100 text-2xl text-primary-600 dark:bg-primary-900/40">
                  {f.icon}
                </div>
                <h3 className="mb-2 font-semibold">{f.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{f.desc}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
