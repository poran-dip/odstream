// Left column of the settings modal: brightness / contrast / saturation.
// Changes are local until "Save Settings" is clicked in the modal.

import type { Dispatch, SetStateAction } from "react";
import type { VideoSettings } from "../../../utils/storage";

interface DisplaySettingsProps {
  settings: VideoSettings;
  setSettings: Dispatch<SetStateAction<VideoSettings>>;
}

export default function DisplaySettings({
  settings,
  setSettings,
}: DisplaySettingsProps) {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-slate-200">
        Display Settings
      </h3>
      <div className="space-y-6">
        {/* Brightness: -100..100, stored as-is */}
        <SliderSetting
          label="Brightness"
          min="-100"
          max="100"
          value={settings.brightness}
          onChange={(value) => {
            const brightness = value;
            setSettings((prev) => ({ ...prev, brightness }));
          }}
          display={settings.brightness}
        />

        {/* Contrast: slider is 0..300%, stored as 0..3.0 */}
        <SliderSetting
          label="Contrast"
          min="0"
          max="300"
          step="10"
          value={Math.round(settings.contrast * 100)}
          onChange={(value) => {
            const contrast = value / 100;
            setSettings((prev) => ({ ...prev, contrast }));
          }}
          display={`${(settings.contrast * 100).toFixed(0)}%`}
        />

        {/* Saturation: slider is 0..200%, stored as 0..2.0 */}
        <SliderSetting
          label="Saturation"
          min="0"
          max="200"
          step="10"
          value={Math.round(settings.saturation * 100)}
          onChange={(value) => {
            const saturation = value / 100;
            setSettings((prev) => ({ ...prev, saturation }));
          }}
          display={`${(settings.saturation * 100).toFixed(0)}%`}
        />

        {/* Always on for now (annotations are applied while recording) */}
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            id="annotateYOLO"
            checked={true}
            disabled={true}
            className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <label htmlFor="annotateYOLO" className="text-sm text-slate-400">
            Enable YOLO Annotations
          </label>
        </div>
      </div>
    </div>
  );
}

interface SliderSettingProps {
  label: string;
  min: string;
  max: string;
  step?: string;
  value: number;
  /** Receives the slider's raw integer value */
  onChange: (value: number) => void;
  display: string | number;
}

/** Labelled range input with the current value shown underneath. */
function SliderSetting({
  label,
  min,
  max,
  step,
  value,
  onChange,
  display,
}: SliderSettingProps) {
  return (
    <div>
      <label className="block text-sm font-medium mb-2 text-slate-300">
        {label}
      </label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
      />
      <span className="text-sm text-slate-400 mt-1 block">{display}</span>
    </div>
  );
}
