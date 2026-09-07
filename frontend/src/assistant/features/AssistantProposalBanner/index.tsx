import { XMarkIcon } from "@heroicons/react/24/outline";
import Input from "core/components/forms/Input";
import { useTranslation } from "next-i18next";

type Props = {
  label: string;
  message?: string;
  messagePlaceholder?: string;
  onMessageChange?: (message: string) => void;
  onDismiss: () => void;
  onAccept?: () => void;
  acceptDisabled?: boolean;
  className?: string;
};

export default function AssistantProposalBanner({
  label,
  message,
  messagePlaceholder,
  onMessageChange,
  onDismiss,
  onAccept,
  acceptDisabled,
  className,
}: Props) {
  const { t } = useTranslation();

  return (
    <div
      className={`shrink-0 flex items-center justify-between gap-4 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm${className ? ` ${className}` : ""}`}
    >
      <div className="min-w-0 flex-1">
        <span className="font-medium text-blue-700">{label}</span>
        {onMessageChange ? (
          <div className="mt-1">
            <Input
              name="commitMessage"
              value={message ?? ""}
              onChange={(event) => onMessageChange(event.target.value)}
              placeholder={messagePlaceholder}
              fullWidth
            />
          </div>
        ) : (
          message && (
            <p className="truncate text-xs text-blue-600" title={message}>
              {message}
            </p>
          )
        )}
      </div>
      <div className="flex shrink-0 items-center gap-3">
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
