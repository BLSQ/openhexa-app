import {
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/solid";
import { SparklesIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import Textarea from "core/components/forms/Textarea/Textarea";
import { useTranslation } from "next-i18next";
import { useEffect, useRef } from "react";
import {
  GenerateSqlFormInstance,
  GenerateSqlPhase,
} from "./useGenerateSqlForm";

const MAX_TEXTAREA_HEIGHT = 480;

type Props = {
  open: boolean;
  onClose: () => void;
  form: GenerateSqlFormInstance;
  monthlyLimitExceeded: boolean;
};

// Mirrors CreatePipelineUsingAI's layout (icon card, headline, textarea, a
// progress panel, disclaimer) so the two AI-generation experiences feel like
// the same feature. It has a single step rather than a checklist: the
// generate-SQL agent's validated final answer IS the query (delivered as
// `output` on `done`, see GenerateSqlAgent._final_output on the backend), so
// there's no separate "creating X" step to report. No tool visualization
// either way — the agent may call execute_sql internally to test its query,
// but that stays out of this dialog (still persisted on Conversation/Message
// for later), per the ticket's design.
const GenerateSqlDialog = ({
  open,
  onClose,
  form,
  monthlyLimitExceeded,
}: Props) => {
  const { t } = useTranslation();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (open) form.reset();
  }, [open, form.reset]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  }, [form.prompt]);

  const { phase } = form;
  const isActive = phase !== GenerateSqlPhase.Idle;
  const isStreaming = phase === GenerateSqlPhase.Generating;

  const handleClose = () => {
    if (isStreaming) form.cancel();
    onClose();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    form.handleSubmit();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      onSubmit={handleSubmit}
      maxWidth="max-w-2xl"
    >
      <Dialog.Title onClose={handleClose}>{t("Generate a query")}</Dialog.Title>
      <Dialog.Content>
        {monthlyLimitExceeded ? (
          <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {t(
              "You have reached your monthly usage limit for the assistant. Please contact your administrator.",
            )}
          </div>
        ) : (
          <div className="space-y-5">
            <div className="flex flex-col items-center gap-4 py-4 text-center">
              <div className="rounded-xl bg-blue-50 p-4">
                <SparklesIcon className="h-6 w-6 text-blue-500" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">
                  {t("What do you want to query?")}
                </h3>
                <p className="mt-1.5 text-sm text-gray-500">
                  {t(
                    "Describe the data you want in plain language and the AI will write the SQL query for you.",
                  )}
                </p>
              </div>
            </div>
            <div className="mx-auto w-4/5 space-y-4">
              <div className="overflow-hidden rounded-xl border border-gray-300 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">
                <Textarea
                  ref={textareaRef}
                  value={form.prompt}
                  onChange={(e) => form.setPrompt(e.target.value)}
                  placeholder={t(
                    "e.g. Show the 10 most recent records ordered by creation date",
                  )}
                  className="resize-none rounded-none border-0 focus:ring-0"
                  autoFocus
                  rows={6}
                  disabled={isStreaming}
                />
              </div>

              {isActive && (
                <div className="space-y-3 rounded-xl border border-gray-200 bg-gray-50 p-4">
                  <div className="flex items-center gap-3">
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center">
                      {phase === GenerateSqlPhase.Done && (
                        <CheckCircleIcon className="h-5 w-5 text-green-500" />
                      )}
                      {phase === GenerateSqlPhase.Error && (
                        <XCircleIcon className="h-5 w-5 text-red-500" />
                      )}
                      {phase === GenerateSqlPhase.Generating && (
                        <Spinner size="xs" className="text-blue-500" />
                      )}
                    </span>
                    <span
                      className={
                        phase === GenerateSqlPhase.Error
                          ? "text-sm text-red-600"
                          : "text-sm text-gray-700"
                      }
                    >
                      {t("Generating SQL query")}
                    </span>
                  </div>

                  {phase === GenerateSqlPhase.Error && (
                    <div className="mt-2 space-y-2">
                      <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                        {form.error}
                      </div>
                      <button
                        type="button"
                        onClick={form.handleSubmit}
                        className="flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 shadow-xs hover:bg-gray-50"
                      >
                        <ArrowPathIcon className="h-3.5 w-3.5" />
                        {t("Try again")}
                      </button>
                    </div>
                  )}
                  {phase === GenerateSqlPhase.Generating && (
                    <button
                      type="button"
                      onClick={form.cancel}
                      className="mt-1 text-xs text-gray-400 underline underline-offset-2 hover:text-gray-600"
                    >
                      {t("Cancel")}
                    </button>
                  )}
                </div>
              )}
            </div>
            <p className="mt-2 text-center text-xs text-gray-400">
              {t("AI can make mistakes. Always verify important information.")}
            </p>
          </div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button type="button" variant="outlined" onClick={handleClose}>
          {t("Close")}
        </Button>
        {!monthlyLimitExceeded && (
          <Button
            type="submit"
            disabled={isActive || !form.prompt.trim()}
            leadingIcon={isStreaming ? <Spinner size="xs" /> : null}
          >
            {t("Generate")}
          </Button>
        )}
      </Dialog.Actions>
    </Dialog>
  );
};

export default GenerateSqlDialog;
