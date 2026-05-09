import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../lib/api";
import { getToken, clearToken } from "../lib/auth";
import { buttonPrimaryClassName } from "../lib/ui";

type Me = {
  gdrive_connected: boolean;
  gdrive_folder_id: string | null;
  has_cloudinary: boolean;
};

type CloudinaryStatus = {
  has_custom_credentials: boolean;
  cloud_name: string | null;
};

export default function Settings() {
  const navigate = useNavigate();
  const [me, setMe] = useState<Me | null>(null);
  const [cloudinary, setCloudinary] = useState<CloudinaryStatus | null>(null);
  const [cloudForm, setCloudForm] = useState({ cloud_name: "", api_key: "", api_secret: "" });
  const [saving, setSaving] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) { navigate("/login", { replace: true }); return; }
    api.me().then(setMe).catch(() => { clearToken(); navigate("/login", { replace: true }); });
    api.cloudinaryGet().then(setCloudinary).catch(() => {});
  }, [navigate]);

  async function saveCloudinary() {
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await api.cloudinarySet(cloudForm.cloud_name, cloudForm.api_key, cloudForm.api_secret);
      const updated = await api.cloudinaryGet();
      setCloudinary(updated);
      setCloudForm({ cloud_name: "", api_key: "", api_secret: "" });
      setSuccess("cloudinary credentials saved");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "failed to save");
    } finally {
      setSaving(false);
    }
  }

  async function removeCloudinary() {
    try {
      await api.cloudinaryRemove();
      setCloudinary({ has_custom_credentials: false, cloud_name: null });
      setSuccess("switched back to shared account");
    } catch { }
  }

  async function disconnectGdrive() {
    setDisconnecting(true);
    try {
      await api.gdriveDisconnect();
      const updated = await api.me();
      setMe(updated);
    } catch { }
    finally { setDisconnecting(false); }
  }

  function signOut() {
    clearToken();
    navigate("/login", { replace: true });
  }

  if (!me || !cloudinary) {
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
        <Link to="/dashboard" className="text-base font-medium text-[#1c1c1e]">publr</Link>
        <button onClick={signOut} className="text-sm text-[#8e91a0] hover:text-[#1c1c1e] transition-colors">
          sign out
        </button>
      </nav>

      <main className="flex flex-1 flex-col gap-12 py-12 max-w-lg">
        <h1 className="text-3xl font-medium text-[#1c1c1e]">settings</h1>

        {/* Google Drive */}
        <section className="flex flex-col gap-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-[#8e91a0]">google drive</p>
          {me.gdrive_connected ? (
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-2 text-sm text-[#1c1c1e]">
                <span className="h-2 w-2 rounded-full bg-green-400" />
                connected
                {me.gdrive_folder_id && (
                  <span className="font-mono text-xs text-[#8e91a0] ml-1">{me.gdrive_folder_id}</span>
                )}
              </div>
              <button
                onClick={disconnectGdrive}
                disabled={disconnecting}
                className="w-fit text-sm text-red-400 hover:text-red-600 transition-colors"
              >
                {disconnecting ? "disconnecting…" : "disconnect"}
              </button>
            </div>
          ) : (
            <p className="text-sm text-[#8e91a0]">not connected — go to <Link to="/dashboard" className="underline">dashboard</Link> to connect.</p>
          )}
        </section>

        {/* Cloudinary */}
        <section className="flex flex-col gap-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-[#8e91a0]">cloudinary</p>
          {cloudinary.has_custom_credentials ? (
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-2 text-sm text-[#1c1c1e]">
                <span className="h-2 w-2 rounded-full bg-green-400" />
                custom account — <span className="font-mono text-xs">{cloudinary.cloud_name}</span>
              </div>
              <button
                onClick={removeCloudinary}
                className="w-fit text-sm text-red-400 hover:text-red-600 transition-colors"
              >
                switch to shared account
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              <p className="text-sm text-[#8e91a0]">using shared account. add your own credentials to use your Cloudinary account.</p>
              <div className="flex flex-col gap-2">
                {(["cloud_name", "api_key", "api_secret"] as const).map((field) => (
                  <input
                    key={field}
                    type={field === "api_secret" ? "password" : "text"}
                    placeholder={field.replace("_", " ")}
                    value={cloudForm[field]}
                    onChange={(e) => setCloudForm((f) => ({ ...f, [field]: e.target.value }))}
                    className="rounded-[10px] border border-[#e0e2e8] px-4 py-3 text-sm text-[#1c1c1e] outline-none focus:border-[#1c1c1e] transition-colors"
                  />
                ))}
              </div>
              {error && <p className="text-xs text-red-500">{error}</p>}
              {success && <p className="text-xs text-green-500">{success}</p>}
              <button
                onClick={saveCloudinary}
                disabled={saving || !cloudForm.cloud_name || !cloudForm.api_key || !cloudForm.api_secret}
                className={buttonPrimaryClassName}
              >
                {saving ? "saving…" : "save credentials"}
              </button>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
