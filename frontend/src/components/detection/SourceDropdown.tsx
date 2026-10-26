// Header dropdown for picking the active camera source.

import { Camera, ChevronDown } from "lucide-react";
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
    <div className="relative flex-1 lg:w-64 min-w-0">
      {/* Toggle button showing the current source */}
      <button
        title="Camera source"
        onClick={onToggle}
        disabled={isLoading}
        aria-expanded={isOpen}
        className="w-full bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 p-3 rounded-xl transition-all duration-200 hover:scale-105 flex items-center justify-between disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <div className="flex items-center space-x-2 truncate">
          <Camera className="w-5 h-5 text-slate-300 flex-shrink-0" />
          <span className="text-sm text-slate-300 truncate">
            {isLoading ? "Loading..." : selectedSource?.name || "Unknown"}
          </span>
        </div>
        <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
      </button>

      {/* Source list */}
      {isOpen && !isLoading && (
        <div className="absolute top-full left-0 mt-2 w-full lg:w-64 bg-slate-800/90 backdrop-blur-md border border-slate-600/50 rounded-xl shadow-xl z-10">
          {sources.map((source) => (
            <button
              key={source.id}
              onClick={() => onSelect(source)}
              className={`w-full text-left px-4 py-2 text-sm transition-colors first:rounded-t-xl last:rounded-b-xl hover:bg-slate-700/50 ${
                selectedSource?.id === source.id
                  ? "bg-blue-600/20 text-blue-300"
                  : "text-slate-300"
              }`}
            >
              {source.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
