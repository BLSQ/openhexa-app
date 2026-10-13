import { gql } from "@apollo/client";
import {
  ChartBarIcon,
  CodeBracketIcon,
  GlobeAltIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import CreateWithAI, { useAIForm } from "assistant/features/CreateWithAI";
import { InstructionSet } from "assistant/instructions";
import Button from "core/components/Button/Button";
import Dialog from "core/components/Dialog";
import MethodCard from "core/components/MethodCard";
import Spinner from "core/components/Spinner";
import { AssistantToolName, WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { useSupersetInstancesQuery } from "webapps/graphql/queries.generated";
import { getWebappTypeLabel } from "webapps/helpers/webappType";
import { CreateWebappDialog_WorkspaceFragment } from "./CreateWebappDialog.generated";

type CreateWebappDialogProps = {
  open: boolean;
  onClose: () => void;
  workspace: CreateWebappDialog_WorkspaceFragment;
};

const CreateWebappDialog = ({
  open,
  onClose,
  workspace,
}: CreateWebappDialogProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const aiEnabled = workspace.organization?.aiSettings?.enabled ?? false;
  const aiBudgetLimitReached =
    workspace.organization?.aiBudgetLimitReached ?? false;
  const [isAIActive, setIsAIActive] = useState(false);

  const { data: supersetData } = useSupersetInstancesQuery({
    variables: { workspaceSlug: workspace.slug },
    skip: !open,
  });
  const hasSupersetInstances =
    (supersetData?.supersetInstances ?? []).length > 0;

  const aiForm = useAIForm({
    workspaceSlug: workspace.slug,
    instructionSet: InstructionSet.CREATE_WEBAPPS,
    createTool: AssistantToolName.CreateStaticWebapp,
    getRedirectUrl: (toolOutput) => {
      const slug = (toolOutput as { webapp?: { slug?: string } })?.webapp?.slug;
      return slug
        ? `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${encodeURIComponent(slug)}/code`
        : null;
    },
    notCreatedMessage: t(
      "The AI could not create the web app. Please try again.",
    ),
    failedMessage: t("An error occurred while creating the web app"),
  });

  useEffect(() => {
    if (open) {
      setIsAIActive(false);
      aiForm.reset();
    }
  }, [open]);

  const goToForm = (type: WebappType) =>
    router.push({
      pathname: `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/create`,
      query: { type },
    });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-4xl">
      <Dialog.Title onClose={onClose}>
        {isAIActive ? t("Create with AI") : t("Create a web app")}
      </Dialog.Title>
      <Dialog.Content className="space-y-4">
        {isAIActive ? (
          <>
            <button
              onClick={() => setIsAIActive(false)}
              className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800"
            >
              ← {t("Back")}
            </button>
            <CreateWithAI
              form={aiForm}
              labels={{
                description: t(
                  "Describe your web app and the AI will generate the code to get you started.",
                ),
                placeholder: t(
                  "e.g. Create a dashboard that shows the monthly number of malaria cases per district from the workspace database",
                ),
                generatingStep: t("Generating web app code"),
                creatingStep: t("Creating web app"),
                openingStep: t("Opening web app editor"),
              }}
            />
          </>
        ) : (
          <div className="flex gap-3">
            {aiEnabled && (
              <MethodCard
                icon={<SparklesIcon className="h-5 w-5 text-blue-400" />}
                title={t("Create with AI")}
                description={t("Describe what you want, AI writes the code")}
                onClick={() => setIsAIActive(true)}
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
              icon={<CodeBracketIcon className="h-5 w-5 text-blue-400" />}
              title={t("From code")}
              description={t(
                "Write or upload your own HTML, CSS and JavaScript",
              )}
              onClick={() => goToForm(WebappType.Static)}
            />
            {hasSupersetInstances && (
              <MethodCard
                icon={<ChartBarIcon className="h-5 w-5 text-blue-400" />}
                title={getWebappTypeLabel(WebappType.Superset)}
                description={t("Embed a Superset dashboard")}
                onClick={() => goToForm(WebappType.Superset)}
              />
            )}
            <MethodCard
              icon={<GlobeAltIcon className="h-5 w-5 text-blue-400" />}
              title={getWebappTypeLabel(WebappType.Iframe)}
              description={t("Embed an existing website by its URL")}
              onClick={() => goToForm(WebappType.Iframe)}
            />
          </div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant="outlined">
          {t("Close")}
        </Button>
        {isAIActive && (
          <Button
            disabled={aiForm.isSubmitting || !aiForm.prompt.trim()}
            onClick={aiForm.handleSubmit}
            leadingIcon={aiForm.isSubmitting ? <Spinner size="xs" /> : null}
          >
            {t("Create")}
          </Button>
        )}
      </Dialog.Actions>
    </Dialog>
  );
};

CreateWebappDialog.fragments = {
  workspace: gql`
    fragment CreateWebappDialog_workspace on Workspace {
      slug
      organization {
        id
        aiSettings {
          enabled
        }
        aiBudgetLimitReached
      }
    }
  `,
};

export default CreateWebappDialog;
