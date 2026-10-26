// The backend's recordings directory: read it and change it.

import { useState, useCallback } from "react";
import { API_BASE_URL } from "./constants";

interface UseVideoDirectoryArgs {
  setError: (error: string | null) => void;
  loadVideos: (selectVideoId?: string) => Promise<void>;
}

export function useVideoDirectory({
  setError,
  loadVideos,
}: UseVideoDirectoryArgs) {
  const [showPathDialog, setShowPathDialog] = useState(false);
  const [newPath, setNewPath] = useState("");
  const [currentPath, setCurrentPath] = useState("");

  /** Read the current video directory from the backend config. */
  const loadConfig = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/config`);
      const data = await response.json();
      if (data.success) {
        setCurrentPath(data.video_path);
      }
    } catch (error) {
      console.error("Error loading config:", error);
    }
  }, []);

  const handlePathChange = async () => {
    if (!newPath.trim()) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/config/path`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          path: newPath.trim(),
        }),
      });

      const data = await response.json();

      if (data.success) {
        setCurrentPath(data.path);
        setShowPathDialog(false);
        setNewPath("");
        // Reload videos from new path
        await loadVideos();
      } else {
        setError(data.error || "Failed to change path");
      }
    } catch (error) {
      setError("Failed to change path");
      console.error("Error changing path:", error);
    }
  };

  /** Open the dialog pre-filled with the current path. */
  const openPathDialog = () => {
    setNewPath(currentPath);
    setShowPathDialog(true);
  };

  return {
    showPathDialog,
    setShowPathDialog,
    newPath,
    setNewPath,
    currentPath,
    loadConfig,
    handlePathChange,
    openPathDialog,
  };
}
