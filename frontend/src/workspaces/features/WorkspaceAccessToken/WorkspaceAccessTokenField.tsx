import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import Textarea from "core/components/forms/Textarea";
import { useTranslation } from "next-i18next";
import useWorkspaceAccessToken from "./useWorkspaceAccessToken";

type WorkspaceAccessTokenFieldProps = {
  workspaceSlug: string;
  canGenerate: boolean;
};

/**
 * The access token of a workspace, as the single value of a form field.
 *
 * Unlike the table cell, there is nothing to scan past here: the token is what
 * the surrounding step asks for, so it is shown in full rather than masked.
 */
const WorkspaceAccessTokenField = (props: WorkspaceAccessTokenFieldProps) => {
  const { workspaceSlug, canGenerate } = props;
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

  if (!revealedToken) {
    return (
      <Button variant="secondary" onClick={toggle} disabled={loading}>
        {t("Show")}
      </Button>
    );
  }

  // The copy button sits in the field, as Input does with its trailing icon, but
  // at the top of a block that is several rows tall. pr-10 is what reserves room
  // for it, so no part of the token ever ends up underneath it.
  // There is nothing to hide the token behind here: the dialog is open to hand it
  // over, and it starts hidden again the next time it is opened.
  return (
    <div className="relative w-full">
      {/* Five rows so that even a temporary token, the longest one, is visible
          without scrolling. */}
      <Textarea
        className="pr-10 font-mono"
        rows={5}
        value={revealedToken}
        readOnly
        onFocus={(event) => event.target.select()}
      />
      <div className="absolute top-0 right-0 inline-flex items-center pt-2.5 pr-2.5">
        <Clipboard iconClassName="h-4 w-4" value={revealedToken} />
      </div>
    </div>
  );
};

export default WorkspaceAccessTokenField;
