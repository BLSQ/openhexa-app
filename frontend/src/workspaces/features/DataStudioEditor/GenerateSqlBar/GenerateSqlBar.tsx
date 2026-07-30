import { SparklesIcon } from "@heroicons/react/24/outline";
import { XCircleIcon } from "@heroicons/react/24/solid";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { FormEvent, KeyboardEvent, useEffect, useRef } from "react";
import {
  GenerateSqlFormInstance,
  GenerateSqlPhase,
} from "./useGenerateSqlForm";

type Props = {
  open: boolean;
  onClose: () => void;
  form: GenerateSqlFormInstance;
  monthlyLimitExceeded: boolean;
};

// Inline bar docked under the toolbar, rather than a modal: generating a
// query is a quick, low-stakes action that shouldn't take over the screen or
// block the editor behind it.
const GenerateSqlBar = ({
  open,
  onClose,
  form,
  monthlyLimitExceeded,
}: Props) => {
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      form.reset();
      inputRef.current?.focus();
    }
  }, [open, form.reset]);

  if (!open) {
    return null;
  }

  const { phase } = form;
  const isGenerating = phase === GenerateSqlPhase.Generating;

  const handleClose = () => {
    if (isGenerating) form.cancel();
    onClose();
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    form.handleSubmit();
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === "Escape") handleClose();
  };

  return (
    <div className="shrink-0 border-b border-gray-200 bg-gray-50 px-3 py-2">
      {monthlyLimitExceeded ? (
        <div className="flex items-center justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <span>
            {t(
              "You have reached your monthly usage limit for the assistant. Please contact your administrator.",
            )}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 font-medium underline underline-offset-2 hover:text-red-800"
          >
            {t("Close")}
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white pl-3 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500">
            <SparklesIcon className="h-4 w-4 shrink-0 text-indigo-500" />
            <input
              ref={inputRef}
              type="text"
              value={form.prompt}
              onChange={(event) => form.setPrompt(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t("Describe what you'd like to query…")}
              disabled={isGenerating}
              className="h-10 min-w-0 flex-1 border-0 bg-transparent text-sm text-gray-900 placeholder-gray-400 focus:ring-0 focus:outline-hidden disabled:cursor-not-allowed"
            />
            <button
              type="button"
              onClick={handleClose}
              className="shrink-0 px-1 text-xs font-medium text-gray-500 hover:text-gray-700"
            >
              {t("Cancel")}
            </button>
            <button
              type="submit"
              disabled={isGenerating || !form.prompt.trim()}
              className="m-1 inline-flex h-8 shrink-0 items-center gap-1.5 rounded-md bg-indigo-600 px-3 text-xs font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-indigo-300"
            >
              {isGenerating ? (
                <Spinner size="xs" className="text-white" />
              ) : (
                <SparklesIcon className="h-3.5 w-3.5" />
              )}
              {isGenerating ? t("Generating…") : t("Generate")}
            </button>
          </div>
          {phase === GenerateSqlPhase.Error && (
            <div className="mt-1.5 flex items-center gap-1.5 text-xs text-red-600">
              <XCircleIcon className="h-3.5 w-3.5 shrink-0" />
              <span>{form.error}</span>
              <button
                type="button"
                onClick={form.handleSubmit}
                className="font-medium underline underline-offset-2 hover:text-red-800"
              >
                {t("Try again")}
              </button>
            </div>
          )}
        </form>
      )}
    </div>
  );
};

export default GenerateSqlBar;
