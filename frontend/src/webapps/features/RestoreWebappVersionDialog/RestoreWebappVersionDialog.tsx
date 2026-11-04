import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { useState } from "react";
import { Trans, useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import { useRestoreWebappVersionMutation } from "webapps/graphql/mutations.generated";

type RestoreWebappVersionDialogProps = {
  open: boolean;
  onClose: () => void;
  webappId: string;
  versionId: string | null;
  onRestored?: () => void;
};

const RestoreWebappVersionDialog = ({
  open,
  onClose,
  webappId,
  versionId,
  onRestored,
}: RestoreWebappVersionDialogProps) => {
  const { t } = useTranslation();
  const [isRestoring, setIsRestoring] = useState(false);
  const [restoreWebappVersion] = useRestoreWebappVersionMutation();
  const shortId = versionId?.substring(0, 7) ?? "";

  const handleConfirm = async () => {
    if (!versionId || isRestoring) return;
    setIsRestoring(true);
    try {
      const { data } = await restoreWebappVersion({
        variables: { input: { id: webappId, versionId } },
        // Every mounted versions list (history, detail header) reloads so the
        // restore commit shows up as the latest and published one.
        refetchQueries: ["WebappVersions"],
        awaitRefetchQueries: true,
      });
      if (data?.restoreWebappVersion?.success) {
        toast.success(t("Version restored and live"));
        onRestored?.();
        onClose();
      } else {
        toast.error(t("Failed to restore version"));
      }
    } catch {
      toast.error(t("Failed to restore version"));
    } finally {
      setIsRestoring(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} persistent={isRestoring}>
      <Dialog.Title>{t("Restore this version")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>
          <Trans>
            A new version with the content of <b>{shortId}</b> will be created
            and go live. The current latest version stays in the history.
          </Trans>
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose} disabled={isRestoring}>
          {t("Cancel")}
        </Button>
        <Button
          onClick={handleConfirm}
          disabled={isRestoring}
          data-testid="confirm-restore"
        >
          {isRestoring && <Spinner size="xs" className="mr-1" />}
          {isRestoring ? t("Restoring...") : t("Restore")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default RestoreWebappVersionDialog;
