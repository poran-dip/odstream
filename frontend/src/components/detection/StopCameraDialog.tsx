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
    <div className="backdrop">
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="stop-camera-title"
        aria-describedby="stop-camera-desc"
        className="panel w-full max-w-md p-6"
      >
        <h2 id="stop-camera-title" className="text-lg font-semibold">
          Stop the camera for everyone?
        </h2>
        <p id="stop-camera-desc" className="mt-2 text-silt">
          The camera is shared. Stopping it ends the live feed on every computer
          connected to this server.
        </p>

        <div className="mt-6 flex justify-end gap-2">
          <button type="button" onClick={onCancel} className="btn-secondary">
            Keep running
          </button>
          <button type="button" onClick={onConfirm} className="btn-danger">
            Stop camera
          </button>
        </div>
      </div>
    </div>
  );
}
