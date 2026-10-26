// Helpers for matching the backend's active camera source to the frontend's
// list of known sources.

import type { CameraSource } from "./storage";

/**
 * Find the known source that corresponds to the backend's source.
 * Local sources match by device index, remote sources by URL.
 */
export const findMatchingSource = (
  backendSource: CameraSource,
  availableSources: CameraSource[],
): CameraSource | null => {
  return (
    availableSources.find((src) => {
      if (src.type === "local" && backendSource.type === "local") {
        return src.index === backendSource.index;
      }
      if (src.type === "remote" && backendSource.type === "remote") {
        return src.url === backendSource.url;
      }
      return false;
    }) || null
  );
};

/**
 * Build a placeholder source for a backend source that isn't in our list
 * (e.g. a camera index or URL set from another client).
 */
export const createTempSource = (backendSource: CameraSource): CameraSource =>
  backendSource.type === "local"
    ? {
        id: `temp-local-${backendSource.index}`,
        name: `Camera ${backendSource.index}`,
        type: "local",
        index: backendSource.index,
      }
    : {
        id: `temp-remote-${Date.now()}`,
        name: "Remote Camera",
        type: "remote",
        url: backendSource.url,
      };
