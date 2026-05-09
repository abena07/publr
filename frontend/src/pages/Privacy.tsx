import { Link } from "react-router-dom";

const CONTACT = import.meta.env.VITE_CONTACT_EMAIL as string | undefined;
const LAST_UPDATED = "April 18, 2026";

export default function Privacy() {
  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-[1280px] flex-col px-8 lowercase">
      <nav className="flex min-h-16 items-center justify-between border-b border-[#e0e2e8]">
        <Link to="/" className="text-base font-medium text-[#1c1c1e]">publr</Link>
      </nav>

      <main className="flex flex-1 flex-col gap-8 py-16 max-w-xl text-sm text-[#1c1c1e] leading-relaxed">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-medium">privacy policy</h1>
          <p className="text-[#8e91a0]">last updated: {LAST_UPDATED}</p>
        </div>

        <p className="text-[#555a6a]">
          publr is a service that helps you publish images from google drive to instagram. this policy describes how we handle information when you use publr.
        </p>

        {CONTACT ? (
          <p><span className="font-medium">contact:</span> <a href={`mailto:${CONTACT}`} className="underline">{CONTACT}</a></p>
        ) : (
          <p className="text-[#555a6a]"><span className="font-medium text-[#1c1c1e]">contact:</span> for privacy requests, email the operator of this publr deployment.</p>
        )}

        <section className="flex flex-col gap-3">
          <h2 className="font-medium text-base">information we collect</h2>
          <p className="text-[#555a6a]">we store your instagram access token and instagram professional account id so we can publish photos to your instagram account on your behalf after you connect instagram through meta's login.</p>
          <ul className="flex flex-col gap-2 text-[#555a6a] list-disc list-inside">
            <li><span className="font-medium text-[#1c1c1e]">account identifiers.</span> we create and store a unique user id when you sign in with meta (instagram).</li>
            <li><span className="font-medium text-[#1c1c1e]">instagram connection data.</span> we store your instagram professional account identifier and access tokens issued by meta, used only to authenticate and publish media as you direct.</li>
            <li><span className="font-medium text-[#1c1c1e]">google drive connection data.</span> if you connect google drive, we store oauth tokens and the folder id you configure to list and read image files you choose to sync.</li>
            <li><span className="font-medium text-[#1c1c1e]">operational data.</span> we may persist google drive file identifiers and related urls to avoid duplicate processing and retry failed uploads.</li>
            <li><span className="font-medium text-[#1c1c1e]">session tokens.</span> we issue signed session tokens (jwts) so your client can call authenticated api routes.</li>
          </ul>
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="font-medium text-base">how we use information</h2>
          <p className="text-[#555a6a]">we use the data above only to operate publr: authenticate you, read images from your selected google drive folder, upload processed images to our image host, and publish to your instagram account.</p>
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="font-medium text-base">third-party services</h2>
          <ul className="flex flex-col gap-2 text-[#555a6a] list-disc list-inside">
            <li><span className="font-medium text-[#1c1c1e]">meta (facebook / instagram)</span> for instagram login and publishing.</li>
            <li><span className="font-medium text-[#1c1c1e]">google</span> for google drive access when you connect drive.</li>
            <li><span className="font-medium text-[#1c1c1e]">cloudinary</span> for hosting uploaded images used in the publishing flow.</li>
            <li><span className="font-medium text-[#1c1c1e]">hosting and database vendors</span> that run the application and postgresql.</li>
          </ul>
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="font-medium text-base">retention</h2>
          <p className="text-[#555a6a]">we retain account and token data until you disconnect your accounts, ask us to delete your data, or we delete it as part of routine service changes.</p>
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="font-medium text-base">security</h2>
          <p className="text-[#555a6a]">we use industry-standard measures including transport encryption (https), protecting secrets via environment configuration, and storing tokens only as needed.</p>
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="font-medium text-base">your choices</h2>
          <p className="text-[#555a6a]">you can stop processing by revoking publr's access in your meta and google account security settings. you may contact us to request access to or deletion of your personal information.</p>
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="font-medium text-base">children</h2>
          <p className="text-[#555a6a]">publr is not directed to children under 13, and we do not knowingly collect personal information from children.</p>
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="font-medium text-base">changes</h2>
          <p className="text-[#555a6a]">we may update this policy from time to time and will adjust the last updated date when we do.</p>
        </section>
      </main>

      <footer className="flex w-full shrink-0 items-center justify-between border-t border-[#e0e2e8] px-8 py-10 text-sm text-[#a5a8b5]">
        <span>© 2026 publr</span>
      </footer>
    </div>
  );
}
