import { ArrowLeft, Zap } from "lucide-react";
import type { ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  description?: string;
  showBackButton?: boolean;
  onBack?: () => void;
  rightActions?: ReactNode;
};

export default function PageHeader({
  title,
  description,
  showBackButton = false,
  onBack,
  rightActions
}: PageHeaderProps) {
  return (
    <>
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center space-x-4">
          {showBackButton &&
            <button
              onClick={onBack}
              className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 p-3 rounded-xl transition-all duration-200 hover:scale-105"
            >
              <ArrowLeft className="w-5 h-5 text-slate-300" />
            </button>
          }
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl">
            <Zap className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              {title}
            </h1>
            {description &&
              <p className="text-slate-400 mt-1">{description}</p>
            }
          </div>
        </div>
        
        {rightActions && (
          <div className="flex items-center space-x-3">
            {rightActions}
          </div>
        )}
      </div>
    </>
  );
}