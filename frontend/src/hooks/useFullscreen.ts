// Full screen for any element, with orientation lock and an iOS fallback.
//
// 1. Uses the Fullscreen API (incl. the webkit-prefixed version) when the
//    browser allows it for this element.
// 2. On phones, then tries to lock the screen orientation to match the
//    content (e.g. rotate to landscape for a landscape camera feed). Android
//    browsers support this; desktop browsers and iOS reject it, which is fine.
// 3. iPhone Safari only allows full screen for <video> elements, so for
//    anything else this falls back to a full-window overlay ("fallback" mode)
//    that the caller styles with `isFullscreen`. Escape closes it.

import { type RefObject, useCallback, useEffect, useState } from "react";

type Orientation = "landscape" | "portrait";

// Prefixed APIs (older Safari / iPad) aren't in the DOM typings
type WebkitElement = HTMLElement & {
  webkitRequestFullscreen?: () => Promise<void> | void;
};
type WebkitDocument = Document & {
  webkitFullscreenElement?: Element | null;
  webkitExitFullscreen?: () => Promise<void> | void;
};
// ScreenOrientation.lock/unlock are missing from some DOM typings
type LockableOrientation = ScreenOrientation & {
  lock?: (orientation: Orientation) => Promise<void>;
  unlock?: () => void;
};

const doc = () => document as WebkitDocument;
const currentFullscreenElement = () =>
  doc().fullscreenElement ?? doc().webkitFullscreenElement ?? null;
const orientation = () =>
  (typeof screen !== "undefined" ? screen.orientation : undefined) as
    | LockableOrientation
    | undefined;

async function lockOrientation(target: Orientation) {
  try {
    await orientation()?.lock?.(target);
  } catch {
    // Not supported (desktop, iOS) or not allowed - keep the current rotation
  }
}

function unlockOrientation() {
  try {
    orientation()?.unlock?.();
  } catch {
    // Nothing to unlock
  }
}

export function useFullscreen<T extends HTMLElement>(ref: RefObject<T | null>) {
  const [isNative, setIsNative] = useState(false);
  const [isFallback, setIsFallback] = useState(false);

  // Track native full screen (also catches the user pressing Esc / back)
  useEffect(() => {
    const onChange = () => {
      const active =
        ref.current !== null && currentFullscreenElement() === ref.current;
      setIsNative(active);
      if (!active) unlockOrientation();
    };
    document.addEventListener("fullscreenchange", onChange);
    document.addEventListener("webkitfullscreenchange", onChange);
    return () => {
      document.removeEventListener("fullscreenchange", onChange);
      document.removeEventListener("webkitfullscreenchange", onChange);
    };
  }, [ref]);

  // Fallback overlay: Esc closes it, and the page behind it can't scroll
  useEffect(() => {
    if (!isFallback) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsFallback(false);
    };
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKey);
    };
  }, [isFallback]);

  /** Enter full screen, rotating to `fit` on devices that allow it. */
  const enter = useCallback(
    async (fit?: Orientation) => {
      const el = ref.current as WebkitElement | null;
      if (!el) return;

      const request = el.requestFullscreen ?? el.webkitRequestFullscreen;
      if (request) {
        try {
          await request.call(el);
          if (fit) await lockOrientation(fit);
          return;
        } catch {
          // Refused (e.g. iPhone for non-video elements) - use the overlay
        }
      }
      setIsFallback(true);
    },
    [ref],
  );

  const exit = useCallback(async () => {
    if (isFallback) {
      setIsFallback(false);
      return;
    }
    if (!currentFullscreenElement()) return;
    const d = doc();
    try {
      await (d.exitFullscreen ?? d.webkitExitFullscreen)?.call(d);
    } catch {
      // Already left full screen
    }
  }, [isFallback]);

  const isFullscreen = isNative || isFallback;

  const toggle = useCallback(
    (fit?: Orientation) => (isFullscreen ? exit() : enter(fit)),
    [isFullscreen, enter, exit],
  );

  return { isFullscreen, enter, exit, toggle };
}
