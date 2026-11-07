// Top bar shared by both pages: optional back button, IITG logo, wordmark
// and page-specific actions on the right.

import { ArrowLeft } from "lucide-react";
import type { ReactNode } from "react";
import IITG from "../assets/iitg.svg";

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
  rightActions,
}: PageHeaderProps) {
  return (
    <header className="mb-5 flex flex-col gap-4 border-b border-line pb-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 items-center gap-3">
        {showBackButton && (
          <button
            type="button"
            onClick={onBack}
            title="Back"
            aria-label="Back"
            className="icon-btn"
          >
            <ArrowLeft className="size-5" />
          </button>
        )}
        <img
          src={IITG}
          alt="IIT Guwahati"
          title="IIT Guwahati"
          className="size-10 shrink-0 rounded-md bg-white p-0.5"
        />
        <div className="min-w-0">
          {/* Wordmark: Archivo at its widest */}
          <h1 className="font-stretch-125% text-xl font-bold leading-tight tracking-tight sm:text-2xl">
            {title}
          </h1>
          {description && (
            <p className="truncate text-sm text-silt">{description}</p>
          )}
        </div>
      </div>

      {rightActions && (
        <div className="flex w-full items-center gap-2 sm:w-auto">
          {rightActions}
        </div>
      )}
    </header>
  );
}
