// Settings modal: display settings (left) + camera sources (right).

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
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-800/90 backdrop-blur-md border border-slate-600/50 rounded-2xl p-6 w-200 max-w-[90vw] max-h-[80vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-6 text-slate-100">Settings</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Side - Display Settings */}
          <DisplaySettings settings={settings} setSettings={setSettings} />

          {/* Right Side - Camera Sources */}
          <CameraSourcesSettings {...sourceProps} />
        </div>

        <div className="flex justify-between mt-8">
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
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            {saving ? "Saving..." : "Save Settings"}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
