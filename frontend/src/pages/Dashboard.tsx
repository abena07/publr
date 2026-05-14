import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../lib/api";
import { getToken, clearToken } from "../lib/auth";
import { buttonPrimaryClassName } from "../lib/ui";

const BASE = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

type Me = {
  id: string;
  instagram_connected: boolean;
  gdrive_connected: boolean;
  gdrive_folder_id: string | null;
  has_cloudinary: boolean;
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [me, setMe] = useState<Me | null>(null);
  const [photos, setPhotos] = useState<string[]>([]);
  const [folderInput, setFolderInput] = useState("");
  const [saving, setSaving] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) { navigate("/login", { replace: true }); return; }
    api.me().then(setMe).catch(() => { clearToken(); navigate("/login", { replace: true }); });
  }, [navigate]);

  useEffect(() => {
    if (me?.gdrive_connected) {
      api.photos().then((r) => setPhotos(r.photos)).catch(() => {});
    }
  }, [me]);

  // After GDrive OAuth redirect back, trigger connect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("gdrive") === "connected") {
      window.history.replaceState({}, "", "/dashboard");
      api.gdriveConnect().then(() => api.me().then(setMe)).catch(() => {});
    }
  }, []);

  function signOut() {
    clearToken();
    navigate("/login", { replace: true });
  }

  async function saveFolder() {
    if (!folderInput.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await api.gdriveSetFolder(folderInput.trim());
      await api.gdriveConnect();
      const updated = await api.me();
      setMe(updated);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "failed to save folder");
    } finally {
      setSaving(false);
    }
  }

  async function connectGdrive() {
    setConnecting(true);
    const token = getToken();
    window.location.href = `${BASE}/auth/gdrive/start?token=${token}`;
  }

  if (!me) {
    return (
      <div className="flex min-h-dvh items-center justify-center text-sm text-[#8e91a0]">
        loading…
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-[1280px] flex-col px-8">
      {/* Nav */}
      <nav className="flex min-h-16 items-center justify-between border-b border-[#e0e2e8]">
        <span className="text-base font-medium text-[#1c1c1e]">publr</span>
        <div className="flex items-center gap-6 text-sm">
          <Link to="/settings" className="text-[#8e91a0] hover:text-[#1c1c1e] transition-colors">
            settings
          </Link>
          <button onClick={signOut} className="text-[#8e91a0] hover:text-[#1c1c1e] transition-colors text-sm">
            sign out
          </button>
        </div>
      </nav>

      <main className="flex flex-1 flex-col gap-12 py-12">
        {/* Step 1: Connect GDrive */}
        {!me.gdrive_connected && !me.gdrive_folder_id && (
          <section className="flex flex-col gap-4 max-w-md">
            <p className="text-xs font-semibold uppercase tracking-widest text-[#8e91a0]">step 1</p>
            <h2 className="text-2xl font-medium text-[#1c1c1e]">Connect Google Drive</h2>
            <p className="text-sm text-[#555a6a] leading-relaxed">
              Grant publr read access to your Google Drive so it can watch your folder for new photos.
            </p>
            <button
              onClick={connectGdrive}
              disabled={connecting}
              className={buttonPrimaryClassName}
            >
              {connecting ? "redirecting…" : "connect google drive"}
            </button>
          </section>
        )}

        {/* Step 2: Set folder */}
        {me.gdrive_connected && !me.gdrive_folder_id && (
          <section className="flex flex-col gap-4 max-w-md">
            <p className="text-xs font-semibold uppercase tracking-widest text-[#8e91a0]">step 2</p>
            <h2 className="text-2xl font-medium text-[#1c1c1e]">Pick your Drive folder</h2>
            <p className="text-sm text-[#555a6a] leading-relaxed">
              Copy your folder link and paste it below
            </p>
            <input
              type="text"
              value={folderInput}
              onChange={(e) => setFolderInput(e.target.value)}
              placeholder="folder ID"
              className="rounded-[10px] border border-[#e0e2e8] px-4 py-3 text-sm text-[#1c1c1e] outline-none focus:border-[#1c1c1e] transition-colors"
            />
            {error && <p className="text-xs text-red-500">{error}</p>}
            <button onClick={saveFolder} disabled={saving} className={buttonPrimaryClassName}>
              {saving ? "saving…" : "save folder"}
            </button>
          </section>
        )}

        {/* Step 3: Photos grid */}
        {me.gdrive_connected && me.gdrive_folder_id && (
          <section className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
              <div className="flex flex-col gap-1">
                <h2 className="text-2xl font-medium text-[#1c1c1e]">your photos</h2>
                <p className="text-sm text-[#8e91a0]">
                  watching folder <span className="font-mono text-xs">{me.gdrive_folder_id}</span>
                </p>
              </div>
            </div>
            {photos.length === 0 ? (
              <p className="text-sm text-[#8e91a0]">
                no photos yet — drop an image into your Drive folder and it'll appear here after the next sync.
              </p>
            ) : (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
                {photos.map((url) => (
                  <img
                    key={url}
                    src={url}
                    alt=""
                    className="aspect-square w-full rounded-xl object-cover"
                  />
                ))}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
