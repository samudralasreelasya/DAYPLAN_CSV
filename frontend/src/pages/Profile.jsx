import { FiUser, FiMail } from "react-icons/fi";
import { useAuth } from "../context/AuthContext.jsx";
import { Card, SectionHeading } from "../components/UI.jsx";

export default function Profile() {
  const { user } = useAuth();

  return (
    <section className="mx-auto max-w-2xl px-5 py-16">
      <SectionHeading eyebrow="Account" title="My Profile" />
      <Card className="flex items-center gap-6">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-accent-500 text-3xl font-bold text-white">
          {user?.name?.[0]?.toUpperCase()}
        </div>
        <div className="space-y-2">
          <p className="flex items-center gap-2 font-semibold"><FiUser /> {user?.name}</p>
          <p className="flex items-center gap-2 text-slate-500"><FiMail /> {user?.email}</p>
        </div>
      </Card>
    </section>
  );
}
