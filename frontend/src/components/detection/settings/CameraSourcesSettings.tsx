// Right column of the settings modal: add a custom source and list all
// sources (built-in ones are read-only, custom ones can be deleted).

import { Plus, Trash2 } from "lucide-react";
import { DEFAULT_SOURCES } from "../../../utils/config";
import type { CameraSource } from "../../../utils/storage";

interface CameraSourcesSettingsProps {
  customSources: CameraSource[];
  newSourceName: string;
  setNewSourceName: (value: string) => void;
  newSourceUrl: string;
  setNewSourceUrl: (value: string) => void;
  onAddSource: () => void;
  onDeleteSource: (id: string) => void;
}

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
    <section>
      <h3 className="font-semibold">Camera sources</h3>

      {/* Sources list: built-in first, then the user's own */}
      <ul className="mt-3 divide-y divide-line rounded-md border border-line">
        {DEFAULT_SOURCES.map((source) => (
          <SourceRow key={source.id} source={source} />
        ))}
        {customSources.map((source) => (
          <SourceRow key={source.id} source={source}>
            <button
              type="button"
              onClick={() => onDeleteSource(source.id)}
              aria-label={`Delete ${source.name}`}
              title="Delete source"
              className="-m-1 rounded-md p-1 text-silt transition-colors hover:text-signal"
            >
              <Trash2 className="size-4" />
            </button>
          </SourceRow>
        ))}
      </ul>

      {/* Add New Source */}
      <h4 className="mt-5 text-sm font-medium">Add a stream</h4>
      <p className="mt-0.5 text-sm text-silt">
        Any MJPEG or snapshot URL, e.g. another ODStream remote.
      </p>
      <div className="mt-3 space-y-2">
        <input
          type="text"
          placeholder="Name"
          aria-label="Source name"
          value={newSourceName}
          onChange={(e) => setNewSourceName(e.target.value)}
          className="field"
        />
        <input
          type="url"
          placeholder="http://host:5000/api/video_feed"
          aria-label="Stream URL"
          value={newSourceUrl}
          onChange={(e) => setNewSourceUrl(e.target.value)}
          className="field"
        />
        <button
          type="button"
          onClick={onAddSource}
          disabled={!newSourceName.trim() || !newSourceUrl.trim()}
          className="btn-secondary w-full"
        >
          <Plus className="size-4" />
          Add source
        </button>
      </div>
    </section>
  );
}

/** Source name, its device index (local) or URL (remote), and its type. */
function SourceRow({
  source,
  children,
}: {
  source: CameraSource;
  children?: React.ReactNode;
}) {
  return (
    <li className="flex items-center gap-3 px-3 py-2.5">
      <div className="min-w-0 flex-1">
        <p className="truncate">{source.name}</p>
        <p className="truncate text-sm text-silt">
          {source.type === "local" ? `Device ${source.index}` : source.url}
        </p>
      </div>
      <span className="shrink-0 text-sm text-silt capitalize">
        {source.type}
      </span>
      {children}
    </li>
  );
}
