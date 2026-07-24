import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FiUser, FiMail, FiLock } from "react-icons/fi";
import { useAuth } from "../context/AuthContext.jsx";
import { ErrorBanner } from "../components/UI.jsx";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form.name, form.email, form.password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-5 py-16">
      <h1 className="section-title text-center">Create Account</h1>
      <p className="mt-2 text-center text-slate-500 dark:text-slate-400">Join DayPlan to save and manage your trips.</p>

      <form onSubmit={handleSubmit} className="glass-card mt-8 space-y-4 p-8">
        {error && <ErrorBanner message={error} />}
        <label className="block">
          <span className="mb-1 flex items-center gap-2 text-sm font-medium"><FiUser /> Full Name</span>
          <input name="name" required value={form.name} onChange={handleChange} className="input-field" />
        </label>
        <label className="block">
          <span className="mb-1 flex items-center gap-2 text-sm font-medium"><FiMail /> Email</span>
          <input type="email" name="email" required value={form.email} onChange={handleChange} className="input-field" />
        </label>
        <label className="block">
          <span className="mb-1 flex items-center gap-2 text-sm font-medium"><FiLock /> Password</span>
          <input type="password" name="password" required minLength={6} value={form.password} onChange={handleChange} className="input-field" />
        </label>
        <button type="submit" disabled={loading} className="btn-primary w-full justify-center disabled:opacity-60">
          {loading ? "Creating account..." : "Sign Up"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        Already have an account? <Link to="/login" className="font-semibold text-primary-600">Log in</Link>
      </p>
    </section>
  );
}
