// Modal for changing the backend's recordings directory.

interface PathDialogProps {
  currentPath: string;
  newPath: string;
  setNewPath: (value: string) => void;
  onCancel: () => void;
  onConfirm: () => void;
}

export default function PathDialog({
  currentPath,
  newPath,
  setNewPath,
  onCancel,
  onConfirm,
}: PathDialogProps) {
  return (
    <div className="backdrop">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="path-dialog-title"
        className="panel w-full max-w-md p-6"
      >
        <h2 id="path-dialog-title" className="text-lg font-semibold">
          Change recordings folder
        </h2>
        <p className="mt-2 text-sm text-silt wrap-break-word">
          The library lists video files from this folder on the computer running
          the backend. Currently: {currentPath}
        </p>
        <label htmlFor="path-input" className="mt-5 block text-sm font-medium">
          Folder path
        </label>
        <input
          id="path-input"
          type="text"
          value={newPath ?? ""}
          onChange={(e) => setNewPath(e.target.value)}
          placeholder="D:/Videos/"
          className="field mt-2"
        />
        <div className="mt-6 flex justify-end gap-2">
          <button type="button" onClick={onCancel} className="btn-secondary">
            Cancel
          </button>
          <button type="button" onClick={onConfirm} className="btn-primary">
            Change folder
          </button>
        </div>
      </div>
    </div>
  );
}
