import { Link } from "react-router-dom";
import { buttonPrimaryClassName } from "../lib/ui";

const steps = [
  {
    n: "01",
    title: "Link Instagram & your site",
    desc: "Connect Instagram and where your photos live on the web so publr can publish to both in one flow.",
  },
  {
    n: "02",
    title: "Pick your Drive folder",
    desc: "Choose one Google Drive folder & use it as the inbox for any image you want to go live.",
  },
  {
    n: "03",
    title: "Drop a file & you’re done",
    desc: "Upload a picture to that folder. publr syncs it to your site and posts it to Instagram.",
  },
];

export default function Landing() {
  return (
    <div className="mx-auto flex min-h-dvh w-full min-w-0 max-w-[1280px] flex-1 flex-col self-center px-8 lowercase">
      {/* Nav — marketing top bar: canvas, ~64px, hairline border */}
      <nav className="flex min-h-16 w-full min-w-0 shrink-0 items-center justify-between gap-4 border-b border-[#e0e2e8]">
        <span className="shrink-0 text-base font-medium tracking-tight text-[#1c1c1e]">publr</span>
        <div className="flex shrink-0 items-center text-sm">
          <Link to="/login" className={buttonPrimaryClassName}>
            get started
          </Link>
        </div>
      </nav>

      <main className="flex flex-1 flex-col">
        {/* Hero — hero-band: generous padding, centered stack */}
        <section className="flex shrink-0 flex-col items-center justify-center gap-12 pb-28 pt-16 text-center sm:gap-14 sm:pb-32 sm:pt-20 lg:gap-16 lg:pb-36 lg:pt-[120px]">
          <h1 className="relative z-0 max-w-3xl shrink-0 text-center text-[length:clamp(2.25rem,6vw,5rem)] font-medium leading-[1.12] tracking-[-0.02em] text-[#1c1c1e] sm:leading-[1.08]">
            you upload. 
            <br />
            <span className="font-medium">we publish.</span>
          </h1>
          <p className="max-w-xl shrink-0 text-lg font-normal leading-[1.5] text-[#555a6a]">
            Drop a photo into your Drive folder. publr handles the rest.
          </p>
          <div className="flex flex-col items-center gap-3">
            <Link to="/login" className={`${buttonPrimaryClassName} self-center`}>
              get started
            </Link>
            <div className="flex items-center gap-4 text-sm text-[#8e91a0]">
              <Link to="/join" className="hover:text-[#1c1c1e] transition-colors">
                join the beta
              </Link>
              <span>·</span>
              <Link to="/setup" className="hover:text-[#1c1c1e] transition-colors">
                what do i need?
              </Link>
            </div>
          </div>
        </section>

        {/* How it works */}
        <section className="w-full shrink-0 border-t border-[#e0e2e8] py-16">
          <header className="mb-10 sm:mb-14">
            <p className="text-[11px] font-semibold leading-[1.4] tracking-[0.08em] text-[#8e91a0]">
              how it works
            </p>
          </header>
          <div className="grid w-full grid-cols-1 gap-12 md:grid-cols-3 md:gap-14">
            {steps.map((s) => (
              <div key={s.n} className="flex min-h-0 flex-col gap-6">
                <span className="font-mono text-xs leading-none tabular-nums text-[#8e91a0]">{s.n}</span>
                <h3 className="text-[22px] font-medium leading-[1.3] text-[#1c1c1e]">{s.title}</h3>
                <p className="text-sm font-normal leading-[1.5] text-[#555a6a]">{s.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* footer-region */}
      <footer className="flex w-full shrink-0 flex-wrap items-center justify-between gap-6 border-[#e0e2e8] border-t text-sm font-normal leading-[1.5] text-[#a5a8b5] px-12 py-10">
        <span>© 2026 publr</span>
        <div className="flex gap-6">
          <Link to="/docs" className="shrink-0 py-1 transition-colors hover:text-[#1c1c1e]">
            docs
          </Link>
          <Link to="/privacy" className="shrink-0 py-1 transition-colors hover:text-[#1c1c1e]">
            privacy
          </Link>
        </div>
      </footer>
    </div>
  );
}
