import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from "lucide-react";
import { useEffect, useRef } from "react";

export type ToastType = "success" | "error" | "warning" | "info";

export interface ToastDisplayProps {
  message: string;
  type?: ToastType;
  onClose?: () => void;
}

// Icon + accent colour per type. The toast itself is a neutral panel with a
// coloured edge so it reads clearly over the video without shouting.
const TOAST_STYLES: Record<
  ToastType,
  { Icon: typeof Info; accent: string; edge: string }
> = {
  success: { Icon: CheckCircle, accent: "text-kelp", edge: "border-l-kelp" },
  error: { Icon: AlertCircle, accent: "text-signal", edge: "border-l-signal" },
  warning: {
    Icon: AlertTriangle,
    accent: "text-buoy",
    edge: "border-l-buoy",
  },
  info: { Icon: Info, accent: "text-silt", edge: "border-l-silt" },
};

const ToastDisplay: React.FC<ToastDisplayProps> = ({
  message,
  type = "info",
  onClose,
}) => {
  // Keep the latest onClose in a ref so the auto-close timer only restarts
  // when the message changes. Callers pass inline arrows (a new function on
  // every render), which would otherwise reset the 5s timer on each render.
  const onCloseRef = useRef(onClose);
  useEffect(() => {
    onCloseRef.current = onClose;
  });

  useEffect(() => {
    if (!message || !onCloseRef.current) return;

    const timeout = setTimeout(() => {
      onCloseRef.current?.();
    }, 5000);

    return () => clearTimeout(timeout);
  }, [message]);

  if (!message) return null;

  const { Icon, accent, edge } = TOAST_STYLES[type];

  return (
    <div
      role={type === "error" ? "alert" : "status"}
      className="fixed bottom-4 left-4 right-4 z-9999 sm:left-auto sm:w-full sm:max-w-sm"
    >
      <div
        className={`panel flex items-start gap-3 border-l-4 bg-raised p-4 ${edge}`}
      >
        <Icon className={`mt-0.5 size-5 shrink-0 ${accent}`} />
        <p className="min-w-0 flex-1 text-sm leading-relaxed wrap-break-word">
          {message}
        </p>

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Dismiss"
            className="-m-1 shrink-0 rounded-md p-1 text-silt transition-colors hover:text-foam"
          >
            <X className="size-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default ToastDisplay;
