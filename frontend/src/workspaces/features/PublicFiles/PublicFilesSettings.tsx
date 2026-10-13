import { gql } from "@apollo/client";
import Clipboard from "core/components/Clipboard";
import DataCard from "core/components/DataCard";
import Switch from "core/components/Switch";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import { useUpdateWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import { PublicFilesSettings_WorkspaceFragment } from "./PublicFilesSettings.generated";
import { PUBLIC_FOLDER } from "./publicFiles";

type PublicFilesSettingsProps = {
  workspace: PublicFilesSettings_WorkspaceFragment;
};

const PublicFilesSettings = ({ workspace }: PublicFilesSettingsProps) => {
  const { t } = useTranslation();
  const [updateWorkspace, { loading }] = useUpdateWorkspaceMutation();
  const canManage = workspace.permissions.managePublicFiles;

  const onChange = async (enabled: boolean) => {
    const { data } = await updateWorkspace({
      variables: {
        input: { slug: workspace.slug, publicFilesEnabled: enabled },
      },
    });
    if (!data?.updateWorkspace.success) {
      toast.error(t("The public files setting could not be updated"));
    }
  };

  return (
    <DataCard item={workspace} className="w-full">
      <DataCard.Section title={t("Public files")}>
        <Switch
          checked={workspace.publicFilesEnabled}
          onChange={onChange}
          disabled={!canManage || loading}
          label={t("Serve the public folder to anyone with a link")}
        />
        <p className="mt-2 text-sm text-gray-500">
          {t(
            'When enabled, every file in the top-level "{{folder}}" folder of the workspace files can be read by anyone who has its link, without an OpenHEXA account. Use it for the data public web apps need, and nothing else.',
            { folder: PUBLIC_FOLDER },
          )}
        </p>
        {!canManage && (
          <p className="mt-1 text-sm text-gray-500">
            {t(
              "Only the administrators and owners of the organization can change this setting.",
            )}
          </p>
        )}
        {workspace.publicFilesEnabled && (
          <div className="mt-3 flex items-center gap-2 text-sm">
            <span className="text-gray-600">{t("Base URL")}</span>
            <code className="rounded-sm bg-gray-50 px-1.5 py-0.5 text-gray-800">
              {workspace.publicFilesUrl}
            </code>
            <Clipboard value={workspace.publicFilesUrl} />
          </div>
        )}
      </DataCard.Section>
    </DataCard>
  );
};

PublicFilesSettings.fragments = {
  workspace: gql`
    fragment PublicFilesSettings_workspace on Workspace {
      slug
      publicFilesEnabled
      publicFilesUrl
      permissions {
        managePublicFiles
      }
    }
  `,
};

export default PublicFilesSettings;
