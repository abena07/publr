import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { buttonPrimaryClassName } from "../lib/ui";

export default function Join() {
  const [email, setEmail] = useState("");
  const [facebook, setFacebook] = useState("");
  const [remaining, setRemaining] = useState<number | null>(null);
  const [position, setPosition] = useState<number | null>(null);
  const [inBeta, setInBeta] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.waitlistCount().then((r) => setRemaining(r.remaining)).catch(() => {});
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const r = await api.waitlistJoin(email.trim(), facebook.trim());
      setPosition(r.position);
      setInBeta(r.in_beta);
      setRemaining((prev) => (prev !== null ? Math.max(0, prev - 1) : null));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-dvh w-full min-w-0 max-w-[1280px] flex-1 flex-col self-center px-8 lowercase">
      <nav className="flex min-h-16 w-full shrink-0 items-center justify-between border-b border-[#e0e2e8]">
        <Link to="/" className="text-base font-medium text-[#1c1c1e]">
          publr
        </Link>
        <Link to="/login" className={buttonPrimaryClassName}>
          get started
        </Link>
      </nav>

      <main className="mx-auto flex w-full min-w-0 max-w-md flex-1 flex-col justify-center gap-8 py-16">
        {position ? (
          <div className="flex flex-col gap-4">
            <p className="font-mono text-xs text-[#8e91a0]">{String(position).padStart(2, "0")}</p>
            <h1 className="text-3xl font-medium text-[#1c1c1e]">you're on the list.</h1>
            <p className="text-sm text-[#555a6a] leading-relaxed">
              {inBeta
                ? `you're number ${position}. i'll add you as a tester and reach out to get you started.`
                : `you're number ${position} on the list. the first 25 spots are taken but i'll reach out if one opens up.`}
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            <div className="flex flex-col gap-3">
              {remaining !== null && (
                <p className="font-mono text-xs text-[#8e91a0]">{remaining} of 25 spots left</p>
              )}
              <h1 className="text-3xl font-medium text-[#1c1c1e]">join the beta.</h1>
              <p className="text-sm text-[#555a6a] leading-relaxed">
                drop your google email and your facebook profile link. the profile link looks like facebook.com/yourname. you'll also need a{" "}
                <a href="https://developers.facebook.com" target="_blank" rel="noopener noreferrer" className="underline text-[#1c1c1e]">facebook developer account</a>
                
              </p>
            </div>

            <form onSubmit={submit} className="flex flex-col gap-3">
              <input
                type="email"
                required
                placeholder="google email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="rounded-[10px] border border-[#e0e2e8] px-4 py-3 text-sm text-[#1c1c1e] outline-none focus:border-[#1c1c1e] transition-colors"
              />
              <input
                type="text"
                required
                placeholder="facebook.com/yourname"
                value={facebook}
                onChange={(e) => setFacebook(e.target.value)}
                className="rounded-[10px] border border-[#e0e2e8] px-4 py-3 text-sm text-[#1c1c1e] outline-none focus:border-[#1c1c1e] transition-colors"
              />
              {error && <p className="text-xs text-red-500">{error}</p>}
              <button
                type="submit"
                disabled={submitting || !email || !facebook}
                className={buttonPrimaryClassName}
              >
                {submitting ? "joining…" : "join"}
              </button>
            </form>
          </div>
        )}
      </main>

      <footer className="flex w-full shrink-0 flex-wrap items-center justify-between gap-6 border-t border-[#e0e2e8] px-8 py-10 text-sm text-[#a5a8b5] sm:px-12 sm:py-10">
        <span>© 2026 publr</span>
        <Link to="/privacy" className="transition-colors hover:text-[#1c1c1e]">
          privacy
        </Link>
      </footer>
    </div>
  );
}
