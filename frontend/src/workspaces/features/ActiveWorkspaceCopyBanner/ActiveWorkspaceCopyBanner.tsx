import { useTranslation } from "next-i18next";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import { DuplicateWorkspaceDialog_RunFragment } from "workspaces/features/DuplicateWorkspaceDialog/DuplicateWorkspaceDialog.generated";

type ActiveWorkspaceCopyBannerProps = {
  run: DuplicateWorkspaceDialog_RunFragment;
  onViewProgress(): void;
};

/**
 * Shows the user's copy that is still queued or running, which is otherwise
 * invisible once its dialog is closed.
 */
const ActiveWorkspaceCopyBanner = ({
  run,
  onViewProgress,
}: ActiveWorkspaceCopyBannerProps) => {
  const { t } = useTranslation();
  return (
    <div
      role="status"
      className="mb-4 flex items-center gap-3 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800"
    >
      <Spinner size="xs" />
      <span className="flex-1">
        {t("Copying {{source}} into {{name}}…", {
          source: run.sourceWorkspace?.name ?? run.sourceWorkspaceSlug,
          name: run.targetWorkspaceName,
        })}
      </span>
      <Button variant="white" size="sm" onClick={onViewProgress}>
        {t("View progress")}
      </Button>
    </div>
  );
};

export default ActiveWorkspaceCopyBanner;
