import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FiMail, FiLock } from "react-icons/fi";
import { useAuth } from "../context/AuthContext.jsx";
import { ErrorBanner } from "../components/UI.jsx";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-5 py-16">
      <h1 className="section-title text-center">Welcome Back</h1>
      <p className="mt-2 text-center text-slate-500 dark:text-slate-400">Log in to access your saved trips.</p>

      <form onSubmit={handleSubmit} className="glass-card mt-8 space-y-4 p-8">
        {error && <ErrorBanner message={error} />}
        <label className="block">
          <span className="mb-1 flex items-center gap-2 text-sm font-medium"><FiMail /> Email</span>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" />
        </label>
        <label className="block">
          <span className="mb-1 flex items-center gap-2 text-sm font-medium"><FiLock /> Password</span>
          <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" />
        </label>
        <button type="submit" disabled={loading} className="btn-primary w-full justify-center disabled:opacity-60">
          {loading ? "Logging in..." : "Log In"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        Don't have an account? <Link to="/register" className="font-semibold text-primary-600">Sign up</Link>
      </p>
    </section>
  );
}
