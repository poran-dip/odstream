// Left column of the settings modal: brightness / contrast / saturation.
// Changes are local until "Save image settings" is clicked in the modal.

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
    <section>
      <h3 className="font-semibold">Image</h3>
      <p className="mt-1 text-sm text-silt">
        Applied to the live feed, snapshots and recordings.
      </p>

      <div className="mt-5 space-y-5">
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
        <div className="flex items-start gap-3">
          <input
            type="checkbox"
            id="annotateYOLO"
            checked={true}
            disabled={true}
            className="mt-1 size-4 accent-buoy disabled:cursor-not-allowed"
          />
          <label htmlFor="annotateYOLO" className="text-sm text-silt">
            Draw detection boxes. Always on while recording.
          </label>
        </div>
      </div>
    </section>
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

/** Labelled range input with its current value at the end of the label row. */
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
      <div className="mb-2 flex items-baseline justify-between">
        <label htmlFor={label} className="text-sm font-medium">
          {label}
        </label>
        <span className="text-sm tabular-nums text-silt">{display}</span>
      </div>
      <input
        id={label}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value, 10))}
        className="w-full cursor-pointer"
      />
    </div>
  );
}
