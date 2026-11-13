import { gql } from "@apollo/client";
import { FolderIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Link from "core/components/Link";
import { Trans, useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { ReactNode, useState } from "react";
import { toast } from "react-toastify";
import { createBucketFolder } from "workspaces/helpers/bucket";
import { PublicFolderPlaceholder_WorkspaceFragment } from "./PublicFolderPlaceholder.generated";

type PublicFolderPlaceholderProps = {
  workspace: PublicFolderPlaceholder_WorkspaceFragment;
};

/**
 * Whether the placeholder has something to show. Kept outside of the component because
 * the data grid renders an extra row as soon as it receives an element, even an empty one.
 */
export const shouldShowPublicFolderPlaceholder = ({
  publicFiles,
  permissions,
}: PublicFolderPlaceholder_WorkspaceFragment) =>
  Boolean(publicFiles && !publicFiles.folderExists && permissions.createObject);

/**
 * Greyed-out "public" folder shown at the root of the filesystem while the folder does not
 * exist, so that members learn about public files and can take the next step.
 */
const PublicFolderPlaceholder = ({
  workspace,
}: PublicFolderPlaceholderProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);
  const { publicFiles, permissions } = workspace;

  const createFolder = async () => {
    setIsCreating(true);
    try {
      const folder = await createBucketFolder(workspace.slug, "public");
      await router.push(
        `/workspaces/${encodeURIComponent(workspace.slug)}/files/${folder.key}`,
      );
    } catch {
      toast.error(t("An error occurred while creating the folder."));
    } finally {
      setIsCreating(false);
    }
  };

  let description: ReactNode;
  if (publicFiles?.url) {
    description = t("Create this folder and put files in it to share publicly");
  } else if (permissions.managePublicFiles) {
    description = (
      <Trans>
        <Link
          href={`/workspaces/${encodeURIComponent(workspace.slug)}/settings`}
        >
          Enable public files
        </Link>{" "}
        and create this folder to start sharing files publicly
      </Trans>
    );
  } else {
    description = t(
      "Enable public files and create this folder to start sharing files publicly",
    );
  }

  return (
    <div className="flex items-center gap-3">
      <FolderIcon className="h-5 w-5 flex-shrink-0 text-gray-300" />
      <span className="font-medium text-gray-400">public</span>
      <span className="text-gray-400">{description}</span>
      <div className="ml-auto flex-shrink-0">
        <Button
          size="sm"
          variant="secondary"
          onClick={createFolder}
          disabled={isCreating}
        >
          {t("Create folder")}
        </Button>
      </div>
    </div>
  );
};

PublicFolderPlaceholder.fragments = {
  workspace: gql`
    fragment PublicFolderPlaceholder_workspace on Workspace {
      slug
      publicFiles {
        url
        folderExists
      }
      permissions {
        createObject
        managePublicFiles
      }
    }
  `,
};

export default PublicFolderPlaceholder;
