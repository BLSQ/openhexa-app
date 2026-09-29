import { gql } from "@apollo/client";
import {
  ChartBarSquareIcon,
  CodeBracketIcon,
  SparklesIcon,
  WindowIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import Button from "core/components/Button/Button";
import Dialog from "core/components/Dialog";
import { WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { ReactNode, useEffect, useState } from "react";
import { useSupersetInstancesQuery } from "webapps/graphql/queries.generated";
import { CreateWebappDialog_WorkspaceFragment } from "./CreateWebappDialog.generated";
import CreateWebappUsingAI from "./CreateWebappUsingAI/CreateWebappUsingAI";

type Method = "ai" | null;

type MethodCardProps = {
  icon: ReactNode;
  title: string;
  description: string;
  disabled?: boolean;
  note?: string;
  onClick: () => void;
};

const MethodCard = ({
  icon,
  title,
  description,
  disabled,
  note,
  onClick,
}: MethodCardProps) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={clsx(
      "flex flex-col items-start rounded-xl border border-gray-200 bg-white p-5 text-left shadow-sm transition-all",
      disabled
        ? "cursor-not-allowed opacity-60"
        : "hover:border-blue-400 hover:bg-blue-50 hover:shadow-md",
    )}
  >
    <div className="mb-4 rounded-lg bg-blue-50 p-2.5">{icon}</div>
    <span className="font-semibold text-gray-900">{title}</span>
    <span className="mt-1 text-sm leading-relaxed text-gray-500">
      {description}
    </span>
    {note && (
      <span className="mt-2 text-xs font-medium text-amber-600">{note}</span>
    )}
  </button>
);

type CreateWebappDialogProps = {
  open: boolean;
  onClose: () => void;
  workspace: CreateWebappDialog_WorkspaceFragment;
};

const CreateWebappDialog = (props: CreateWebappDialogProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { open, onClose, workspace } = props;
  const aiEnabled = workspace.organization?.aiSettings?.enabled ?? false;
  const aiBudgetLimitReached =
    workspace.organization?.aiBudgetLimitReached ?? false;

  const [activeMethod, setActiveMethod] = useState<Method>(null);
  const [prompt, setPrompt] = useState("");

  const { data: supersetData } = useSupersetInstancesQuery({
    variables: { workspaceSlug: workspace.slug },
    skip: !open,
  });
  const hasSupersetInstances =
    (supersetData?.supersetInstances?.length ?? 0) > 0;

  useEffect(() => {
    if (open) {
      setActiveMethod(null);
      setPrompt("");
    }
  }, [open]);

  const goToCreatePage = (type: WebappType) => {
    router
      .push(
        `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/create?type=${type}`,
      )
      .then();
  };

  const TITLES: Record<string, string> = {
    ai: t("Create with AI"),
  };
  const dialogTitle = activeMethod
    ? TITLES[activeMethod]
    : t("Create a web app");

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-3xl">
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

        {activeMethod === null && (
          <div className="grid grid-cols-2 gap-3">
            <MethodCard
              icon={<SparklesIcon className="h-5 w-5 text-blue-400" />}
              title={t("Create with AI")}
              description={t("Describe what you want, AI writes the code")}
              disabled={!aiEnabled || aiBudgetLimitReached}
              note={
                aiBudgetLimitReached
                  ? t("Monthly AI budget reached")
                  : !aiEnabled
                    ? t("AI is not enabled for this organization")
                    : undefined
              }
              onClick={() => setActiveMethod("ai")}
            />
            <MethodCard
              icon={<CodeBracketIcon className="h-5 w-5 text-blue-400" />}
              title={t("From code/files")}
              description={t(
                "Write the code or upload the files of your web app",
              )}
              onClick={() => goToCreatePage(WebappType.Static)}
            />
            <MethodCard
              icon={<ChartBarSquareIcon className="h-5 w-5 text-blue-400" />}
              title={t("Superset")}
              description={t("Embed a dashboard from a Superset instance")}
              disabled={!hasSupersetInstances}
              note={
                hasSupersetInstances
                  ? undefined
                  : t("No Superset instance configured")
              }
              onClick={() => goToCreatePage(WebappType.Superset)}
            />
            <MethodCard
              icon={<WindowIcon className="h-5 w-5 text-blue-400" />}
              title={t("iFrame")}
              description={t("Embed an existing page from its URL")}
              onClick={() => goToCreatePage(WebappType.Iframe)}
            />
          </div>
        )}

        {activeMethod === "ai" && (
          <CreateWebappUsingAI prompt={prompt} onPromptChange={setPrompt} />
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <div className="flex-1" />
        <Button onClick={onClose} variant="outlined">
          {t("Close")}
        </Button>
        {activeMethod === "ai" && (
          <Button disabled={!prompt.trim()}>{t("Create")}</Button>
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
