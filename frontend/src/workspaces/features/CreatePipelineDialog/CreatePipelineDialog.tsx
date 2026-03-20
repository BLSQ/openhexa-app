import { gql } from "@apollo/client";
import Button from "core/components/Button/Button";
import Dialog from "core/components/Dialog";
import { useTranslation } from "next-i18next";
import { useEffect, useState } from "react";
import { CreatePipelineDialog_WorkspaceFragment } from "./CreatePipelineDialog.generated";
import PipelineTemplates from "pipelines/features/PipelineTemplates/PipelineTemplates";
import CreatePipelineUsingCLI from "./CreatePipelineUsingCLI/CreatePipelineUsingCLI";
import CreatePipelineUsingNotebook from "./CreatePipelineUsingNotebook/CreatePipelineUsingNotebook";
import { useNotebookForm } from "./CreatePipelineUsingNotebook/useNotebookForm";
import CreatePipelineUsingAI from "./CreatePipelineUsingAI/CreatePipelineUsingAI";
import { useAIForm } from "./CreatePipelineUsingAI/useAIForm";
import BucketObjectPicker from "../BucketObjectPicker";

type Method = "ai" | "template" | "notebook" | "cli" | null;

type CreatePipelineDialogProps = {
  open: boolean;
  onClose: () => void;
  workspace: CreatePipelineDialog_WorkspaceFragment;
};

const CreatePipelineDialog = (props: CreatePipelineDialogProps) => {
  const { t } = useTranslation();
  const { open, onClose, workspace } = props;

  const [activeMethod, setActiveMethod] = useState<Method>(null);

  const notebookForm = useNotebookForm(workspace);
  const aiForm = useAIForm(workspace);

  useEffect(() => {
    if (open) {
      setActiveMethod(null);
      notebookForm.resetForm();
      aiForm.reset();
    }
  }, [open]);

  const dialogTitle =
    activeMethod === "ai"
      ? t("Create with AI")
      : activeMethod === "template"
        ? t("From Template")
        : activeMethod === "notebook"
          ? t("From Notebook")
          : activeMethod === "cli"
            ? t("From OpenHEXA CLI")
            : t("Create a pipeline");

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={activeMethod === "template" ? "max-w-7/8" : "max-w-4xl"}
    >
      <Dialog.Title onClose={onClose}>{dialogTitle}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <button
          onClick={() => setActiveMethod(null)}
          className={
            activeMethod === null
              ? "hidden"
              : "flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800"
          }
        >
          ← {t("Back")}
        </button>

        <div className={activeMethod !== null ? "hidden" : "space-y-4"}>
          <div className="flex gap-3">
            <button
              onClick={() => setActiveMethod("ai")}
              className="flex flex-1 flex-col items-start rounded-lg border border-gray-200 p-5 text-left transition-colors hover:border-blue-400 hover:bg-blue-50"
            >
              <span className="mb-2 text-xl">✨</span>
              <span className="font-medium text-gray-900">
                {t("Create with AI")}
              </span>
              <span className="mt-1 text-sm text-gray-500">
                {t("Describe what you want, AI writes the code")}
              </span>
            </button>
            <button
              onClick={() => setActiveMethod("template")}
              className="flex flex-1 flex-col items-start rounded-lg border border-gray-200 p-5 text-left transition-colors hover:border-blue-400 hover:bg-blue-50"
            >
              <span className="mb-2 text-xl">📋</span>
              <span className="font-medium text-gray-900">
                {t("From Template")}
              </span>
              <span className="mt-1 text-sm text-gray-500">
                {t("Start from a shared template")}
              </span>
            </button>
            <button
              onClick={() => setActiveMethod("notebook")}
              className="flex flex-1 flex-col items-start rounded-lg border border-gray-200 p-5 text-left transition-colors hover:border-blue-400 hover:bg-blue-50"
            >
              <span className="mb-2 text-xl">📓</span>
              <span className="font-medium text-gray-900">
                {t("From Notebook")}
              </span>
              <span className="mt-1 text-sm text-gray-500">
                {t("Use a Jupyter notebook")}
              </span>
            </button>
          </div>
        </div>

        <div className={activeMethod !== "ai" ? "hidden" : undefined}>
          <CreatePipelineUsingAI form={aiForm} />
        </div>

        <div className={activeMethod !== "template" ? "hidden" : undefined}>
          <PipelineTemplates workspace={workspace} showCard={false} />
        </div>

        <div className={activeMethod !== "notebook" ? "hidden" : undefined}>
          <CreatePipelineUsingNotebook form={notebookForm} workspace={workspace} />
        </div>

        <div className={activeMethod !== "cli" ? "hidden" : undefined}>
          <CreatePipelineUsingCLI open={open} workspace={workspace} />
        </div>
      </Dialog.Content>
      <Dialog.Actions>
        {activeMethod === null && (
          <div className="flex">
            <button
              onClick={() => setActiveMethod("cli")}
              className="text-sm text-blue-600 underline underline-offset-2 hover:text-gray-800"
            >
              {t("From OpenHEXA CLI")} →
            </button>
          </div>
        )}
        <div className="flex-1" />
        <Button onClick={onClose} variant="outlined">
          {t("Close")}
        </Button>
        {activeMethod === "notebook" && (
          <Button
            disabled={notebookForm.isSubmitting}
            onClick={notebookForm.handleSubmit}
          >
            {t("Create")}
          </Button>
        )}
        {activeMethod === "ai" && (
          <Button
            disabled={aiForm.isSubmitting || !aiForm.prompt.trim()}
            onClick={aiForm.handleSubmit}
          >
            {t("Create")}
          </Button>
        )}
      </Dialog.Actions>
    </Dialog>
  );
};

CreatePipelineDialog.fragments = {
  workspace: gql`
    fragment CreatePipelineDialog_workspace on Workspace {
      slug
      ...BucketObjectPicker_workspace
    }
    ${BucketObjectPicker.fragments.workspace}
  `,
};

export default CreatePipelineDialog;
