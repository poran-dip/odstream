// All state and behaviour for the Recordings page, stitched from:
//   useVideoLibrary   - list, selection, load, delete
//   useVideoRename    - inline rename
//   useVideoDirectory - recordings directory (read / change)

import { useEffect } from "react";
import { useVideoLibrary } from "./useVideoLibrary";
import { useVideoRename } from "./useVideoRename";
import { useVideoDirectory } from "./useVideoDirectory";

export function useRecordings() {
  const library = useVideoLibrary();
  const { loadVideos, setError, currentVideo, setCurrentVideo } = library;

  const rename = useVideoRename({
    currentVideo,
    setCurrentVideo,
    setError,
    loadVideos,
  });

  const directory = useVideoDirectory({ setError, loadVideos });
  const { loadConfig } = directory;

  // Load videos on component mount (both callbacks are stable)
  useEffect(() => {
    loadVideos();
    loadConfig();
  }, [loadVideos, loadConfig]);

  return { library, rename, directory };
}
