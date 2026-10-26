// User-defined (remote) camera sources, persisted in localStorage.

import { useState } from "react";
import type { ToastType } from "../../components/ui/ToastDisplay";
import { storageUtils, type CameraSource } from "../../utils/storage";
import { DEFAULT_SOURCES } from "../../utils/config";

interface UseCustomSourcesArgs {
  selectedSource: CameraSource | null;
  setSelectedSource: (source: CameraSource | null) => void;
  showToast: (message: string, type?: ToastType) => void;
}

export function useCustomSources({
  selectedSource,
  setSelectedSource,
  showToast,
}: UseCustomSourcesArgs) {
  const [customSources, setCustomSources] = useState<CameraSource[]>([]);

  // Controlled inputs for the "Add Custom Source" form
  const [newSourceName, setNewSourceName] = useState<string>("");
  const [newSourceUrl, setNewSourceUrl] = useState<string>("");

  /** Built-in sources followed by the user's custom ones. */
  const getAllSources = (): CameraSource[] => {
    return [...DEFAULT_SOURCES, ...customSources];
  };

  const addCustomSource = () => {
    const name = newSourceName.trim();
    const url = newSourceUrl.trim();

    if (!name || !url) {
      return showToast("Name and URL are required", "warning");
    }
    if (!url.includes(".")) return showToast("URL looks wrong?", "warning");

    const newSource = storageUtils.addCustomSource(name, url);
    setCustomSources((prev) => [...prev, newSource]);
    showToast(`${name} added!`, "success");
    setNewSourceName("");
    setNewSourceUrl("");
  };

  const deleteCustomSource = (id: string) => {
    const sourceToDelete = customSources.find((source) => source.id === id);

    storageUtils.removeCustomSource(id);
    setCustomSources((prev) => prev.filter((source) => source.id !== id));

    // If the deleted source was selected, switch to webcam
    if (selectedSource?.id === id) {
      setSelectedSource(DEFAULT_SOURCES[0]);
    }

    const name = sourceToDelete?.name || "Source";
    showToast(`"${name}" deleted!`, "success");
  };

  return {
    customSources,
    setCustomSources,
    newSourceName,
    setNewSourceName,
    newSourceUrl,
    setNewSourceUrl,
    getAllSources,
    addCustomSource,
    deleteCustomSource,
  };
}
