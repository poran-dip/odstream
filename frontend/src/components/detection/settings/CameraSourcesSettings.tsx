// Right column of the settings modal: add a custom source and list all
// sources (built-in ones are read-only, custom ones can be deleted).

import { Plus, Trash2 } from "lucide-react";
import type { CameraSource } from "../../../utils/storage";
import { DEFAULT_SOURCES } from "../../../utils/config";

interface CameraSourcesSettingsProps {
  customSources: CameraSource[];
  newSourceName: string;
  setNewSourceName: (value: string) => void;
  newSourceUrl: string;
  setNewSourceUrl: (value: string) => void;
  onAddSource: () => void;
  onDeleteSource: (id: string) => void;
}

const INPUT_CLASS =
  "w-full bg-slate-800/50 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500";

export default function CameraSourcesSettings({
  customSources,
  newSourceName,
  setNewSourceName,
  newSourceUrl,
  setNewSourceUrl,
  onAddSource,
  onDeleteSource,
}: CameraSourcesSettingsProps) {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-slate-200">
        Camera Sources
      </h3>

      {/* Add New Source */}
      <div className="bg-slate-700/30 rounded-xl p-4 mb-4">
        <h4 className="text-sm font-medium mb-3 text-slate-300">
          Add Custom Source
        </h4>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Source name"
            value={newSourceName}
            onChange={(e) => setNewSourceName(e.target.value)}
            className={INPUT_CLASS}
          />
          <input
            type="url"
            placeholder="Stream URL"
            value={newSourceUrl}
            onChange={(e) => setNewSourceUrl(e.target.value)}
            className={INPUT_CLASS}
          />
          <button
            onClick={onAddSource}
            disabled={!newSourceName.trim() || !newSourceUrl.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Source</span>
          </button>
        </div>
      </div>

      {/* Sources List */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-slate-300">
          Available Sources
        </h4>

        {/* Default Sources */}
        {DEFAULT_SOURCES.map((source) => (
          <div
            key={source.id}
            className="bg-slate-700/20 rounded-lg p-3 flex items-center justify-between"
          >
            <div>
              <SourceDetails source={source} />
            </div>
            <div className="text-xs text-slate-500 capitalize">
              {source.type}
            </div>
          </div>
        ))}

        {/* Custom Sources */}
        {customSources.map((source) => (
          <div
            key={source.id}
            className="bg-slate-700/20 rounded-lg p-3 flex items-center justify-between"
          >
            <div className="flex-1 min-w-0">
              <SourceDetails source={source} />
            </div>
            <div className="flex items-center gap-2">
              <div className="text-xs text-slate-500 capitalize">
                {source.type}
              </div>
              <button
                onClick={() => onDeleteSource(source.id)}
                className="text-red-400 hover:text-red-300 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}

        {customSources.length === 0 && (
          <div className="text-center py-4 text-slate-500 text-sm">
            No custom sources added yet
          </div>
        )}
      </div>
    </div>
  );
}

/** Source name plus its device index (local) or URL (remote). */
function SourceDetails({ source }: { source: CameraSource }) {
  return (
    <>
      <div className="font-medium text-slate-200">{source.name}</div>
      <div className="text-xs text-slate-400 truncate">
        {source.type === "local" ? `Device ${source.index}` : source.url}
      </div>
    </>
  );
}
