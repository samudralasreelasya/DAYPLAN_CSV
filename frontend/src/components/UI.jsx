import { motion } from "framer-motion";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export function Loader({ label = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      <p className="text-sm text-slate-500">{label}</p>
    </div>
  );
}

export function ErrorBanner({ message }) {
  if (!message) return null;
  return (
    <div className="glass-card border-red-200 bg-red-50/80 px-4 py-3 text-sm text-red-600 dark:bg-red-950/40 dark:text-red-300">
      {message}
    </div>
  );
}

export function SectionHeading({ eyebrow, title, subtitle }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="mb-8 text-center"
    >
      {eyebrow && <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-accent-500">{eyebrow}</p>}
      <h2 className="section-title">{title}</h2>
      {subtitle && <p className="mx-auto mt-3 max-w-2xl text-slate-500 dark:text-slate-400">{subtitle}</p>}
    </motion.div>
  );
}

export function Card({ children, className = "" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4 }}
      className={`glass-card p-5 ${className}`}
    >
      {children}
    </motion.div>
  );
}

export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <Loader label="Checking session..." />;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
