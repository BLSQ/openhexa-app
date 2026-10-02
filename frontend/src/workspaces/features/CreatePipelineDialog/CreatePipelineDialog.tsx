import { gql } from "@apollo/client";
import {
  DocumentDuplicateIcon,
  SparklesIcon,
  DocumentTextIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button/Button";
import MethodCard from "core/components/MethodCard";
import Spinner from "core/components/Spinner";
import Dialog from "core/components/Dialog";
import { useTranslation } from "next-i18next";
import PipelineTemplates from "pipelines/features/PipelineTemplates/PipelineTemplates";
import { useEffect, useState } from "react";
import { CreatePipelineDialog_WorkspaceFragment } from "./CreatePipelineDialog.generated";
import CreatePipelineUsingCLI from "./CreatePipelineUsingCLI/CreatePipelineUsingCLI";
import CreatePipelineUsingNotebook from "./CreatePipelineUsingNotebook/CreatePipelineUsingNotebook";
import { useNotebookForm } from "./CreatePipelineUsingNotebook/useNotebookForm";
import CreateWithAI, { useAIForm } from "assistant/features/CreateWithAI";
import { InstructionSet } from "assistant/instructions";
import { AssistantToolName } from "graphql/types";
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
  const aiEnabled = workspace.organization?.aiSettings?.enabled ?? false;
  const aiBudgetLimitReached =
    workspace.organization?.aiBudgetLimitReached ?? false;

  const [activeMethod, setActiveMethod] = useState<Method>(null);

  const notebookForm = useNotebookForm(workspace);
  const aiForm = useAIForm({
    workspaceSlug: workspace.slug,
    instructionSet: InstructionSet.CREATE_PIPELINE,
    createTool: AssistantToolName.CreatePipeline,
    getRedirectUrl: (toolOutput) => {
      const code = (toolOutput as { pipeline?: { code?: string } })?.pipeline
        ?.code;
      return code
        ? `/workspaces/${encodeURIComponent(workspace.slug)}/pipelines/${encodeURIComponent(code)}/code`
        : null;
    },
    notCreatedMessage: t(
      "The AI could not create the pipeline. Please try again.",
    ),
    failedMessage: t("An error occurred while creating the pipeline."),
  });

  useEffect(() => {
    if (open) {
      setActiveMethod(null);
      notebookForm.resetForm();
      aiForm.reset();
    }
  }, [open]);

  const TITLES: Record<string, string> = {
    ai: t("Create with AI"),
    template: t("From Template"),
    notebook: t("From Notebook"),
    cli: t("From OpenHEXA CLI"),
  };
  const dialogTitle = activeMethod
    ? TITLES[activeMethod]
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
            {aiEnabled && (
              <MethodCard
                icon={<SparklesIcon className="h-5 w-5 text-blue-400" />}
                title={t("Create with AI")}
                description={t("Describe what you want, AI writes the code")}
                onClick={() => setActiveMethod("ai")}
                disabled={aiBudgetLimitReached}
                footer={
                  aiBudgetLimitReached && (
                    <span className="mt-2 text-xs font-medium text-amber-600">
                      {t("Monthly AI budget reached")}
                    </span>
                  )
                }
              />
            )}
            <MethodCard
              icon={<DocumentDuplicateIcon className="h-5 w-5 text-blue-400" />}
              title={t("From Template")}
              description={t("Start from a shared template")}
              onClick={() => setActiveMethod("template")}
            />
            <MethodCard
              icon={<DocumentTextIcon className="h-5 w-5 text-blue-400" />}
              title={t("From Notebook")}
              description={t("Use a Jupyter notebook")}
              onClick={() => setActiveMethod("notebook")}
            />
          </div>
        </div>

        {activeMethod === "ai" && (
          <CreateWithAI
            form={aiForm}
            labels={{
              description: t(
                "Describe your pipeline and the AI will generate the code to get you started.",
              ),
              placeholder: t(
                "e.g. Create a pipeline that fetches data from the DHIS2 API, transform it, and save it as a CSV in the workspace",
              ),
              generatingStep: t("Generating pipeline code"),
              creatingStep: t("Creating pipeline"),
              openingStep: t("Opening pipeline editor"),
            }}
          />
        )}

        <div className={activeMethod !== "template" ? "hidden" : undefined}>
          <PipelineTemplates workspace={workspace} showCard={false} />
        </div>

        <div className={activeMethod !== "notebook" ? "hidden" : undefined}>
          <CreatePipelineUsingNotebook
            form={notebookForm}
            workspace={workspace}
          />
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
              className="text-sm ml-2 text-blue-600 underline underline-offset-2 hover:text-gray-800"
            >
              {t("From OpenHEXA CLI")} →
            </button>
          </div>
        )}
        <div className="flex-1" />
        <Button onClick={onClose} variant="outlined">
          {t("Close")}
        </Button>
        {activeMethod === "ai" && (
          <Button
            disabled={aiForm.isSubmitting || !aiForm.prompt.trim()}
            onClick={aiForm.handleSubmit}
            leadingIcon={aiForm.isSubmitting ? <Spinner size="xs" /> : null}
          >
            {t("Create")}
          </Button>
        )}
        {activeMethod === "notebook" && (
          <Button
            disabled={notebookForm.isSubmitting}
            onClick={notebookForm.handleSubmit}
            leadingIcon={
              notebookForm.isSubmitting ? <Spinner size="xs" /> : null
            }
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
      permissions {
        generateToken
      }
      organization {
        id
        aiSettings {
          enabled
        }
        aiBudgetLimitReached
      }
      ...BucketObjectPicker_workspace
    }
    ${BucketObjectPicker.fragments.workspace}
  `,
};

export default CreatePipelineDialog;
