// Full-screen placeholder shown while the current camera source is loaded.

import { LoaderCircle } from "lucide-react";

export default function LoadingScreen() {
  return (
    <div className="grid min-h-screen place-items-center p-6">
      <div className="flex items-center gap-3 text-silt" role="status">
        <LoaderCircle
          className="size-5 text-buoy motion-safe:animate-spin"
          aria-hidden="true"
        />
        <p>Connecting to the camera…</p>
      </div>
    </div>
  );
}
