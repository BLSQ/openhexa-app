import {
  ClockIcon,
  EyeIcon,
  EyeSlashIcon,
  LockClosedIcon,
} from "@heroicons/react/24/outline";
import Clipboard from "core/components/Clipboard";
import Tooltip from "core/components/Tooltip";
import { useTranslation } from "next-i18next";
import useWorkspaceAccessToken from "./useWorkspaceAccessToken";

type WorkspaceAccessTokenCellProps = {
  workspaceSlug: string;
  canGenerate: boolean;
  // Users without a direct membership get an identity token, which expires.
  // Flagging it keeps them from pasting a token that stops working the next day.
  temporary?: boolean;
};

/** The access token of a workspace, as one row of a table of workspaces. */
const WorkspaceAccessTokenCell = (props: WorkspaceAccessTokenCellProps) => {
  const { workspaceSlug, canGenerate, temporary = false } = props;
  const { t } = useTranslation();
  const { revealedToken, loading, toggle } =
    useWorkspaceAccessToken(workspaceSlug);

  if (!canGenerate) {
    return (
      <span className="text-sm italic text-gray-500">
        {t("Not available for viewers")}
      </span>
    );
  }

  return (
    <div className="flex items-start gap-2">
      {/* Both states share this slot, so revealing a token does not move the
          controls. 48ch caps the line at a length that can still be read back
          and compared with a local token; whitespace-normal undoes the
          whitespace-nowrap every DataGrid cell carries, which would otherwise
          keep the token on a single overflowing line. */}
      <div className="w-[48ch] min-w-0 max-w-full whitespace-normal font-mono text-xs">
        {revealedToken ? (
          <code className="block break-all rounded-md bg-gray-50 p-2 ring-1 ring-inset ring-gray-200">
            {revealedToken}
          </code>
        ) : (
          <span className="flex items-center gap-2 py-2 text-gray-500">
            <LockClosedIcon className="h-3 w-3" />
            <span>*********</span>
          </span>
        )}
      </div>
      <div className="flex shrink-0 items-center gap-1 py-2">
        <button
          type="button"
          onClick={toggle}
          disabled={loading}
          title={
            revealedToken
              ? t("Hide the access token")
              : t("Show the access token")
          }
          // p-1 brings the target to the 24px minimum without moving the icon
          className="cursor-pointer p-1 hover:text-blue-500 focus:outline-hidden"
        >
          {revealedToken ? (
            <EyeSlashIcon className="h-4 w-4" />
          ) : (
            <EyeIcon className="h-4 w-4" />
          )}
        </button>
        {revealedToken && (
          <Clipboard iconClassName="h-4 w-4" value={revealedToken} />
        )}
        {temporary && (
          <Tooltip
            label={
              // break-normal: the tooltip breaks words mid-word by default, which
              // this sentence cannot afford as the only explanation of the flag.
              <span className="flex flex-col gap-1 break-normal">
                <span className="font-medium text-gray-900">
                  {t("Temporary")}
                </span>
                {t(
                  "You are not a direct member of this workspace, so this token is temporary: generate a new one once it expires.",
                )}
              </span>
            }
          >
            <span className="flex items-center text-gray-400">
              <ClockIcon className="h-4 w-4" aria-hidden="true" />
              <span className="sr-only">{t("Temporary")}</span>
            </span>
          </Tooltip>
        )}
      </div>
    </div>
  );
};

export default WorkspaceAccessTokenCell;
