// Full-screen placeholder shown while the current camera source is loaded.

export default function LoadingScreen() {
  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-blue-900 to-slate-900 text-white flex items-center justify-center animate-fade-in">
      <div className="text-center space-y-4">
        <div className="relative flex items-center justify-center">
          <div className="absolute animate-ping rounded-full h-16 w-16 bg-blue-500 opacity-50"></div>
          <svg
            className="h-12 w-12 text-blue-400 animate-pulse"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <title>Loading</title>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 5h2l.4 2M7 13h10l1-2H6.4M7 13l1.6 8h6.8l1.6-8M7 13l1-2m3-5h4"
            />
          </svg>
        </div>
        <p className="text-slate-300 text-lg font-light">
          Initializing camera settings...
        </p>
      </div>
    </div>
  );
}
