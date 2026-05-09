import { Link } from "react-router-dom";
import { buttonPrimaryClassName } from "../lib/ui";

const steps = [
  {
    n: "01",
    title: "create a facebook account",
    desc: "you need a personal facebook account first. if you already have one, skip this.",
  },
  {
    n: "02",
    title: "create a facebook page",
    desc: "from your facebook account, create a page. it can be for anything, even just your name. this is different from your personal profile.",
  },
  {
    n: "03",
    title: "switch instagram to a professional account",
    desc: "go to your instagram profile → settings → account → switch to professional account. choose business or creator.",
  },
  {
    n: "04",
    title: "connect instagram to the facebook page",
    desc: "in instagram settings → account → linked accounts → facebook. link it to the page you just created.",
  },
  {
    n: "05",
    title: "have a google account",
    desc: "publr watches a folder in your google drive. any google account works.",
  },
];

export default function Setup() {
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

      <main className="mx-auto flex w-full min-w-0 max-w-xl flex-1 flex-col gap-12 py-16">
        <div className="flex flex-col gap-3">
          <h1 className="text-3xl font-medium text-[#1c1c1e]">before you start</h1>
          <p className="text-sm text-[#555a6a] leading-relaxed">
            publr publishes to instagram through meta's api, which requires a professional account linked to a facebook page. takes about 5 minutes to set up if you haven't already.
          </p>
        </div>

        <div className="flex flex-col gap-10">
          {steps.map((s) => (
            <div key={s.n} className="flex flex-col gap-3">
              <span className="font-mono text-xs text-[#8e91a0]">{s.n}</span>
              <h3 className="text-lg font-medium text-[#1c1c1e]">{s.title}</h3>
              <p className="text-sm text-[#555a6a] leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>

        <Link to="/login" className={`${buttonPrimaryClassName} w-fit`}>
          i'm ready, get started
        </Link>
      </main>

      <footer className="flex w-full shrink-0 flex-wrap items-center justify-between gap-6 border-t border-[#e0e2e8] px-8 py-10 text-sm text-[#a5a8b5] sm:px-12 sm:py-10">
        <span>© 2026 publr</span>
        <a href="/privacy" className="transition-colors hover:text-[#1c1c1e]">
          privacy
        </a>
      </footer>
    </div>
  );
}
