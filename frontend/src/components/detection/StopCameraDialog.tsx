// Confirmation dialog before stopping the camera (affects every client).

interface StopCameraDialogProps {
  onCancel: () => void;
  onConfirm: () => void;
}

export default function StopCameraDialog({
  onCancel,
  onConfirm,
}: StopCameraDialogProps) {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-800/90 backdrop-blur-md border border-slate-600/50 rounded-2xl p-6 w-[500px] max-w-[90vw]">
        <h2 className="text-xl font-bold mb-4 text-slate-100">Stop Camera</h2>
        <p className="text-slate-300 mb-6">
          This will stop camera for <strong>EVERY computer</strong> connected to
          this network. Are you sure you want to proceed?
        </p>

        <div className="flex justify-end space-x-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Stop Camera
          </button>
        </div>
      </div>
    </div>
  );
}
