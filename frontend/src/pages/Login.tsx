import { buttonPrimaryClassName } from "../lib/ui";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

export default function Login() {
  return (
    <div className="flex min-h-dvh w-full flex-1 flex-col items-center justify-center gap-8 px-8 lowercase">
      <div className="flex flex-col items-center gap-3 text-center">
        <span className="text-2xl font-medium text-[#1c1c1e]">publr</span>
        <p className="max-w-xs text-sm font-normal leading-[1.5] text-[#6b6f7e]">
          Connect your Instagram to get started.
        </p>
      </div>
      <a href={`${BACKEND_URL}/auth/instagram`} className={buttonPrimaryClassName}>
        connect instagram
      </a>
    </div>
  );
}
