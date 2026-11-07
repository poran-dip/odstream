// Header dropdown for picking the active camera source.

import { Camera, Check, ChevronDown } from "lucide-react";
import type { CameraSource } from "../../utils/storage";

interface SourceDropdownProps {
  isOpen: boolean;
  onToggle: () => void;
  isLoading: boolean;
  selectedSource: CameraSource | null;
  sources: CameraSource[];
  onSelect: (source: CameraSource) => void;
}

export default function SourceDropdown({
  isOpen,
  onToggle,
  isLoading,
  selectedSource,
  sources,
  onSelect,
}: SourceDropdownProps) {
  return (
    <div className="relative min-w-0 flex-1 sm:w-60 sm:flex-none">
      {/* Toggle button showing the current source */}
      <button
        type="button"
        title="Camera source"
        onClick={onToggle}
        disabled={isLoading}
        aria-expanded={isOpen}
        className="flex h-10 w-full items-center gap-2 rounded-md border border-line bg-hull px-3 text-left transition-colors hover:bg-raised disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Camera className="size-4 shrink-0 text-silt" />
        <span className="min-w-0 flex-1 truncate">
          {isLoading ? "Loading…" : selectedSource?.name || "Unknown"}
        </span>
        <ChevronDown
          className={`size-4 shrink-0 text-silt transition-transform ${isOpen ? "rotate-180" : ""}`}
        />
      </button>

      {/* Source list */}
      {isOpen && !isLoading && (
        <div className="absolute right-0 left-0 top-full z-20 mt-1 overflow-hidden rounded-md border border-line bg-hull py-1 shadow-lg shadow-deep/60">
          {sources.map((source) => {
            const selected = selectedSource?.id === source.id;
            return (
              <button
                type="button"
                aria-pressed={selected}
                key={source.id}
                onClick={() => onSelect(source)}
                className="flex w-full items-center gap-2 px-3 py-2 text-left transition-colors hover:bg-raised"
              >
                <span className="min-w-0 flex-1 truncate">{source.name}</span>
                {selected && <Check className="size-4 shrink-0 text-foam" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
