// NOTE: the Recordings page talks to the backend on localhost directly,
// unlike the rest of the app which uses API_BASE_URL from utils/config
// (built from the runtime-detected IP). Kept as-is during the refactor.
export const API_BASE_URL = "http://localhost:5000/api";

/** URL the <video> element streams a recording from. */
export const getVideoUrl = (filename: string): string => {
  return `${API_BASE_URL}/videos/${encodeURIComponent(filename)}`;
};
