import { AlertCircle, CheckCircle, Info, AlertTriangle, X } from 'lucide-react'
import { useEffect } from 'react'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastDisplayProps {
  message: string
  type?: ToastType
  onClose?: () => void
}

const ToastDisplay: React.FC<ToastDisplayProps> = ({ 
  message, 
  type = 'info', 
  onClose, 
}) => {
  useEffect(() => {
    if (!message || !onClose ) return

    const timeout = setTimeout(() => {
      onClose()
    }, 5000)

    return () => clearTimeout(timeout)
  }, [message, onClose])
  
  if (!message) return null

  const getToastStyles = () => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-green-900/90',
          border: 'border-green-500/50',
          shadow: 'shadow-green-500/25',
          textColor: 'text-green-100',
          iconColor: 'text-green-400',
          hoverBg: 'hover:bg-green-500/20',
          closeColor: 'text-green-400 hover:text-green-200'
        }
      case 'error':
        return {
          bg: 'bg-red-900/90',
          border: 'border-red-500/50',
          shadow: 'shadow-red-500/25',
          textColor: 'text-red-100',
          iconColor: 'text-red-400',
          hoverBg: 'hover:bg-red-500/20',
          closeColor: 'text-red-400 hover:text-red-200'
        }
      case 'warning':
        return {
          bg: 'bg-yellow-900/90',
          border: 'border-yellow-500/50',
          shadow: 'shadow-yellow-500/25',
          textColor: 'text-yellow-100',
          iconColor: 'text-yellow-400',
          hoverBg: 'hover:bg-yellow-500/20',
          closeColor: 'text-yellow-400 hover:text-yellow-200'
        }
      case 'info':
      default:
        return {
          bg: 'bg-blue-900/90',
          border: 'border-blue-500/50',
          shadow: 'shadow-blue-500/25',
          textColor: 'text-blue-100',
          iconColor: 'text-blue-400',
          hoverBg: 'hover:bg-blue-500/20',
          closeColor: 'text-blue-400 hover:text-blue-200'
        }
    }
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
      case 'error':
        return <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
      case 'info':
      default:
        return <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
    }
  }

  const styles = getToastStyles()

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 sm:left-auto sm:right-4 sm:translate-x-0 z-[9999] w-[calc(100vw-2rem)] max-w-sm sm:max-w-md sm:w-full animate-in slide-in-from-bottom-2 duration-300">
      <div className={`${styles.bg} border ${styles.border} backdrop-blur-md rounded-lg p-4 shadow-lg ${styles.shadow}`}>
        <div className="flex items-start space-x-3">
          <div className={styles.iconColor}>
            {getIcon()}
          </div>
          <div className="flex-1 min-w-0">
            <p className={`${styles.textColor} text-sm leading-relaxed break-words`}>
              {message}
            </p>
          </div>
          
          {onClose && (
            <button
              onClick={onClose}
              className={`${styles.closeColor} transition-colors p-1 rounded-md ${styles.hoverBg} flex-shrink-0`}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ToastDisplay