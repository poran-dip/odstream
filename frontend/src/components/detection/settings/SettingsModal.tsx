// Settings modal: image adjustments (left) + camera sources (right).

import { X } from "lucide-react";
import type { Dispatch, SetStateAction } from "react";
import type { CameraSource, VideoSettings } from "../../../utils/storage";
import CameraSourcesSettings from "./CameraSourcesSettings";
import DisplaySettings from "./DisplaySettings";

interface SettingsModalProps {
  settings: VideoSettings;
  setSettings: Dispatch<SetStateAction<VideoSettings>>;
  /** Persist the current display settings to the backend */
  onSave: (settings: Partial<VideoSettings>) => void;
  saving: boolean;
  onClose: () => void;

  // Custom sources
  customSources: CameraSource[];
  newSourceName: string;
  setNewSourceName: (value: string) => void;
  newSourceUrl: string;
  setNewSourceUrl: (value: string) => void;
  onAddSource: () => void;
  onDeleteSource: (id: string) => void;
}

export default function SettingsModal({
  settings,
  setSettings,
  onSave,
  saving,
  onClose,
  ...sourceProps
}: SettingsModalProps) {
  return (
    <div className="backdrop">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="settings-title"
        className="panel flex max-h-[85vh] w-full max-w-3xl flex-col"
      >
        <div className="flex items-center justify-between border-b border-line px-6 py-4">
          <h2 id="settings-title" className="text-lg font-semibold">
            Settings
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close settings"
            className="-m-1 rounded-md p-1 text-silt transition-colors hover:text-foam"
          >
            <X className="size-5" />
          </button>
        </div>

        <div className="grid flex-1 grid-cols-1 gap-x-8 gap-y-6 overflow-y-auto p-6 md:grid-cols-2">
          <DisplaySettings settings={settings} setSettings={setSettings} />
          <CameraSourcesSettings {...sourceProps} />
        </div>

        <div className="flex justify-end gap-2 border-t border-line px-6 py-4">
          <button type="button" onClick={onClose} className="btn-secondary">
            Close
          </button>
          <button
            type="button"
            onClick={() => {
              onSave({
                brightness: settings.brightness,
                contrast: settings.contrast,
                saturation: settings.saturation,
              });
            }}
            disabled={saving}
            className="btn-primary"
          >
            {saving ? "Saving…" : "Save image settings"}
          </button>
        </div>
      </div>
    </div>
  );
}
