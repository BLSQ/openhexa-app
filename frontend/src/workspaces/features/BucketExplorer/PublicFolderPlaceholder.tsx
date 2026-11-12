import { gql } from "@apollo/client";
import { FolderIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Link from "core/components/Link";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { ReactNode, useState } from "react";
import { toast } from "react-toastify";
import { createBucketFolder } from "workspaces/helpers/bucket";
import { PublicFolderPlaceholder_WorkspaceFragment } from "./PublicFolderPlaceholder.generated";

type PublicFolderPlaceholderProps = {
  workspace: PublicFolderPlaceholder_WorkspaceFragment;
};

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

  if (!publicFiles || publicFiles.folderExists) {
    return null;
  }

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

  let description: string;
  let action: ReactNode;
  if (!publicFiles.url) {
    description = t(
      "Share files with anyone who has their link, for example to feed a public web app.",
    );
    if (permissions.managePublicFiles) {
      action = (
        <Link
          href={`/workspaces/${encodeURIComponent(workspace.slug)}/settings`}
        >
          {t("Enable public files")}
        </Link>
      );
    } else if (permissions.createObject) {
      action = t("Ask a workspace admin to enable public files");
    } else {
      return null;
    }
  } else if (permissions.createObject) {
    description = t(
      "Public files are enabled. Create this folder and put the files to share in it.",
    );
    action = (
      <Button
        size="sm"
        variant="secondary"
        onClick={createFolder}
        disabled={isCreating}
      >
        {t("Create folder")}
      </Button>
    );
  } else {
    return null;
  }

  return (
    <div className="flex items-center gap-3">
      <FolderIcon className="h-5 w-5 flex-shrink-0 text-gray-300" />
      <span className="font-medium text-gray-400">public</span>
      <span className="text-gray-400">{description}</span>
      <div className="ml-auto flex-shrink-0">{action}</div>
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
