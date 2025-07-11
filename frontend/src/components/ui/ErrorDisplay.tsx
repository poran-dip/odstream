import { AlertCircle, X } from 'lucide-react'
import { useEffect } from 'react'

interface ErrorDisplayProps {
  error: string
  onClose?: () => void
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onClose }) => {
  useEffect(() => {
    if (!error || !onClose) return

    const timeout = setTimeout(() => {
      onClose()
    }, 5000)

    return () => clearTimeout(timeout)
  }, [error, onClose])
  
  if (!error) return null

  return (
    <div className="fixed bottom-4 right-4 z-9999 max-w-md animate-in slide-in-from-top-2 duration-300">
      <div className="bg-red-900/90 border border-red-500/50 backdrop-blur-md rounded-lg p-4 shadow-lg shadow-red-500/25">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-red-100 text-sm leading-relaxed break-words">{error}</p>
          </div>
          
          {onClose && (
            <button
              onClick={onClose}
              className="text-red-400 hover:text-red-200 transition-colors p-1 rounded-md hover:bg-red-500/20 flex-shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ErrorDisplay