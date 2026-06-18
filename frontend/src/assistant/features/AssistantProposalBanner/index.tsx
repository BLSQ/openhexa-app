import { XMarkIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";

type Props = {
  label: string;
  onDismiss: () => void;
  onAccept?: () => void;
  acceptDisabled?: boolean;
  className?: string;
};

export default function AssistantProposalBanner({
  label,
  onDismiss,
  onAccept,
  acceptDisabled,
  className,
}: Props) {
  const { t } = useTranslation();

  return (
    <div
      className={`shrink-0 mb-2 flex items-center justify-between rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm${className ? ` ${className}` : ""}`}
    >
      <span className="font-medium text-blue-700">{label}</span>
      <div className="flex items-center gap-3">
        {onAccept && (
          <button
            onClick={onAccept}
            disabled={acceptDisabled}
            className="text-xs font-medium text-blue-700 hover:text-blue-900 disabled:opacity-50"
          >
            {t("Apply")}
          </button>
        )}
        <button
          onClick={onDismiss}
          className="flex items-center gap-1 text-blue-500 hover:text-blue-700 text-xs"
        >
          <XMarkIcon className="h-3.5 w-3.5" />
          {t("Dismiss")}
        </button>
      </div>
    </div>
  );
}
