import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { FiMenu, FiX, FiMoon, FiSun, FiUser } from "react-icons/fi";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar({ darkMode, setDarkMode }) {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const links = [
    { to: "/", label: "Home" },
    { to: "/planner", label: "Explore" },
    { to: "/saved-trips", label: "Destinations" },
    { to: "/#about", label: "About" },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-white/30 bg-white/70 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/70">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
        <Link to="/" className="font-display text-2xl font-extrabold text-primary-600">
          Day<span className="text-accent-500">Plan</span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {links.map((l) => (
            <NavLink
              key={l.label}
              to={l.to}
              className={({ isActive }) =>
                `text-sm font-medium transition-colors hover:text-primary-600 ${
                  isActive ? "text-primary-600" : "text-slate-600 dark:text-slate-300"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="rounded-full p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
            aria-label="Toggle dark mode"
          >
            {darkMode ? <FiSun /> : <FiMoon />}
          </button>

          {user ? (
            <div className="flex items-center gap-2">
              <Link to="/profile" className="btn-secondary !px-4 !py-2 text-sm">
                <FiUser /> {user.name?.split(" ")[0]}
              </Link>
              <button
                onClick={() => {
                  logout();
                  navigate("/");
                }}
                className="text-sm font-medium text-slate-500 hover:text-red-500"
              >
                Logout
              </button>
            </div>
          ) : (
            <>
              <Link to="/login" className="text-sm font-medium text-slate-600 dark:text-slate-300">
                Login
              </Link>
              <Link to="/register" className="btn-primary !px-5 !py-2 text-sm">
                Sign Up
              </Link>
            </>
          )}
        </div>

        <button className="md:hidden" onClick={() => setOpen(!open)} aria-label="Toggle menu">
          {open ? <FiX size={24} /> : <FiMenu size={24} />}
        </button>
      </nav>

      {open && (
        <div className="flex flex-col gap-4 border-t border-slate-200 bg-white px-5 py-4 dark:border-slate-800 dark:bg-slate-950 md:hidden">
          {links.map((l) => (
            <Link key={l.label} to={l.to} onClick={() => setOpen(false)} className="text-sm font-medium">
              {l.label}
            </Link>
          ))}
          {user ? (
            <>
              <Link to="/profile" onClick={() => setOpen(false)} className="text-sm font-medium">
                Profile
              </Link>
              <button
                onClick={() => {
                  logout();
                  setOpen(false);
                  navigate("/");
                }}
                className="text-left text-sm font-medium text-red-500"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={() => setOpen(false)} className="text-sm font-medium">
                Login
              </Link>
              <Link to="/register" onClick={() => setOpen(false)} className="btn-primary w-fit !px-5 !py-2 text-sm">
                Sign Up
              </Link>
            </>
          )}
        </div>
      )}
    </header>
  );
}
