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
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-800 border border-slate-600 rounded-2xl p-6 w-full max-w-md">
        <h3 className="text-xl font-semibold mb-4">Change Video Directory</h3>
        <p className="text-sm text-slate-400 mb-4 truncate">
          Currently in:{" "}
          <span className="font-mono text-slate-300">{currentPath}</span>
        </p>
        <input
          type="text"
          value={newPath ?? ""}
          onChange={(e) => setNewPath(e.target.value)}
          placeholder="Enter directory path (e.g., D:/Videos/)"
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <div className="flex justify-end space-x-3 mt-4">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-slate-400 hover:text-slate-300"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl"
          >
            Change Path
          </button>
        </div>
      </div>
    </div>
  );
}
