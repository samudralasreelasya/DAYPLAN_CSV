import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <section className="flex min-h-[60vh] flex-col items-center justify-center px-5 text-center">
      <h1 className="text-6xl font-extrabold text-primary-600">404</h1>
      <p className="mt-3 text-lg text-slate-500">Page not found.</p>
      <Link to="/" className="btn-primary mt-6">Back to Home</Link>
    </section>
  );
}
