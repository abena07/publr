import { Link } from "react-router-dom";

const BASE_URL = "https://publr-production.up.railway.app";

const snippets = [
  {
    label: "react",
    code: `import { useEffect, useState } from 'react';

export default function Photos() {
  const [photos, setPhotos] = useState([]);

  useEffect(() => {
    fetch('${BASE_URL}/api/photos/YOUR_USER_ID')
      .then(r => r.json())
      .then(data => setPhotos(data.photos));
  }, []);

  return (
    <div>
      {photos.map(url => (
        <img key={url} src={url} alt="" />
      ))}
    </div>
  );
}`,
  },
  {
    label: "next.js",
    code: `export default async function Photos() {
  const res = await fetch('${BASE_URL}/api/photos/YOUR_USER_ID', {
    next: { revalidate: 300 },
  });
  const { photos } = await res.json();

  return (
    <div>
      {photos.map((url: string) => (
        <img key={url} src={url} alt="" />
      ))}
    </div>
  );
}`,
  },
  {
    label: "astro",
    code: `---
const res = await fetch('${BASE_URL}/api/photos/YOUR_USER_ID');
const { photos } = await res.json();
---
<div>
  {photos.map((url) => (
    <img src={url} alt="" />
  ))}
</div>`,
  },
  {
    label: "sveltekit",
    code: `// +page.ts
export async function load({ fetch }) {
  const res = await fetch('${BASE_URL}/api/photos/YOUR_USER_ID');
  const { photos } = await res.json();
  return { photos };
}`,
  },
];

export default function Docs() {
  return (
    <div className="mx-auto flex min-h-dvh w-full min-w-0 max-w-[1280px] flex-1 flex-col self-center px-8 lowercase">
      <nav className="flex min-h-16 w-full shrink-0 items-center justify-between border-b border-[#e0e2e8]">
        <Link to="/" className="text-base font-medium text-[#1c1c1e]">
          publr
        </Link>
        <Link to="/login" className="text-sm text-[#8e91a0] transition-colors hover:text-[#1c1c1e]">
          get started
        </Link>
      </nav>

      <main className="mx-auto flex w-full min-w-0 max-w-2xl flex-1 flex-col gap-12 py-16">
        <div className="flex flex-col gap-3">
          <h1 className="text-3xl font-medium text-[#1c1c1e]">show your photos anywhere</h1>
          <p className="text-sm text-[#555a6a] leading-relaxed">
            once publr is running, use the api to pull your photos into any site or framework. no auth needed, just your user id.
          </p>
        </div>

        {/* Endpoint */}
        <section className="flex flex-col gap-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-[#8e91a0]">endpoint</p>
          <div className="rounded-[10px] border border-[#e0e2e8] p-4 font-mono text-sm text-[#1c1c1e]">
            GET {BASE_URL}/api/photos/YOUR_USER_ID
          </div>
          <p className="text-sm text-[#555a6a]">
            returns <span className="font-mono text-xs text-[#1c1c1e]">{"{ photos: string[] }"}</span>, an array of image urls from your watched drive folder.
          </p>
        </section>

        {/* User ID */}
        <section className="flex flex-col gap-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-[#8e91a0]">your user id</p>
          <p className="text-sm text-[#555a6a] leading-relaxed">
            find it in your publr <Link to="/settings" className="underline text-[#1c1c1e]">settings</Link>. replace <span className="font-mono text-xs text-[#1c1c1e]">YOUR_USER_ID</span> in the snippets below with your actual id.
          </p>
        </section>

        {/* Snippets */}
        <section className="flex flex-col gap-6">
          <p className="text-xs font-semibold uppercase tracking-widest text-[#8e91a0]">examples</p>
          {snippets.map((s) => (
            <div key={s.label} className="flex flex-col gap-2">
              <p className="text-sm font-medium text-[#1c1c1e]">{s.label}</p>
              <pre className="overflow-x-auto rounded-[10px] border border-[#e0e2e8] bg-[#f7f8fa] p-4 font-mono text-xs leading-relaxed text-[#1c1c1e]">
                {s.code}
              </pre>
            </div>
          ))}
        </section>
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
