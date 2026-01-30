import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import { useTranslation } from "next-i18next";

type PendingToolCall = {
  id: string;
  toolName: string;
  toolInput: Record<string, unknown>;
};

type ToolApprovalDialogProps = {
  open: boolean;
  pendingToolCall: PendingToolCall | null;
  onApprove: () => void;
  onReject: () => void;
  loading?: boolean;
};

const ToolApprovalDialog = ({
  open,
  pendingToolCall,
  onApprove,
  onReject,
  loading,
}: ToolApprovalDialogProps) => {
  const { t } = useTranslation();

  if (!pendingToolCall) return null;

  const { toolName, toolInput } = pendingToolCall;

  const getToolDescription = () => {
    switch (toolName) {
      case "write_file":
        return t("The assistant wants to write a file");
      case "edit_file":
        return t("The assistant wants to edit a file");
      default:
        return t("The assistant wants to perform an action");
    }
  };

  return (
    <Dialog open={open} onClose={onReject} maxWidth="max-w-xl">
      <Dialog.Title onClose={onReject}>{t("Approve Action")}</Dialog.Title>

      <Dialog.Content>
        <div className="flex items-start gap-3">
          <ExclamationTriangleIcon className="mt-0.5 h-6 w-6 shrink-0 text-amber-500" />
          <div>
            <p className="font-medium text-gray-900">{getToolDescription()}</p>
            <p className="mt-1 text-sm text-gray-600">
              {t("Please review and approve this action before it's executed.")}
            </p>
          </div>
        </div>

        <div className="mt-4 rounded-md bg-gray-50 p-4">
          <dl className="space-y-2 text-sm">
            {toolName === "write_file" && (
              <>
                <div>
                  <dt className="font-medium text-gray-700">{t("File path")}</dt>
                  <dd className="mt-1 font-mono text-gray-900">
                    {toolInput.path as string}
                  </dd>
                </div>
                <div>
                  <dt className="font-medium text-gray-700">
                    {t("Content preview")}
                  </dt>
                  <dd className="mt-1">
                    <pre className="max-h-48 overflow-auto rounded bg-gray-800 p-3 text-xs text-gray-100">
                      {(toolInput.content as string)?.slice(0, 1000)}
                      {(toolInput.content as string)?.length > 1000 && "..."}
                    </pre>
                  </dd>
                </div>
              </>
            )}
            {toolName === "edit_file" && (
              <>
                <div>
                  <dt className="font-medium text-gray-700">{t("File path")}</dt>
                  <dd className="mt-1 font-mono text-gray-900">
                    {toolInput.path as string}
                  </dd>
                </div>
                <div>
                  <dt className="font-medium text-gray-700">{t("Removing")}</dt>
                  <dd className="mt-1">
                    <pre className="max-h-32 overflow-auto rounded bg-red-950 p-3 text-xs text-red-200">
                      {(toolInput.old_string as string)?.slice(0, 1000)}
                      {(toolInput.old_string as string)?.length > 1000 && "..."}
                    </pre>
                  </dd>
                </div>
                <div>
                  <dt className="font-medium text-gray-700">{t("Adding")}</dt>
                  <dd className="mt-1">
                    <pre className="max-h-32 overflow-auto rounded bg-green-950 p-3 text-xs text-green-200">
                      {(toolInput.new_string as string)?.slice(0, 1000)}
                      {(toolInput.new_string as string)?.length > 1000 && "..."}
                    </pre>
                  </dd>
                </div>
              </>
            )}
            {toolName !== "write_file" && toolName !== "edit_file" && (
              <div>
                <dt className="font-medium text-gray-700">{t("Tool")}</dt>
                <dd className="mt-1 font-mono text-gray-900">{toolName}</dd>
                <dt className="mt-2 font-medium text-gray-700">{t("Input")}</dt>
                <dd className="mt-1">
                  <pre className="max-h-48 overflow-auto rounded bg-gray-800 p-3 text-xs text-gray-100">
                    {JSON.stringify(toolInput, null, 2)}
                  </pre>
                </dd>
              </div>
            )}
          </dl>
        </div>
      </Dialog.Content>

      <Dialog.Actions>
        <Button variant="white" onClick={onReject} disabled={loading}>
          {t("Reject")}
        </Button>
        <Button variant="primary" onClick={onApprove} disabled={loading}>
          {loading ? t("Approving...") : t("Approve")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default ToolApprovalDialog;
