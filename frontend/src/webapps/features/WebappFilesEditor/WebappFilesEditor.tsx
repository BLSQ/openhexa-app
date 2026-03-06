import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import { FilesEditor } from "workspaces/features/FilesEditor/FilesEditor";
import { FilesEditor_FileFragment } from "workspaces/features/FilesEditor/FilesEditor.generated";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import { useWebappFilesQuery } from "webapps/graphql/queries.generated";
import Spinner from "core/components/Spinner";

type WebappFilesEditorProps = {
  webappId: string;
  workspaceSlug: string;
  webappSlug: string;
  isEditable: boolean;
};

const WebappFilesEditor = ({
  webappId,
  workspaceSlug,
  webappSlug,
  isEditable,
}: WebappFilesEditorProps) => {
  const { t } = useTranslation();

  const { data, loading, refetch } = useWebappFilesQuery({
    variables: { workspaceSlug, webappSlug },
  });

  const [updateWebapp] = useUpdateWebappMutation();

  const files = data?.webapp?.files ?? [];

  const handleSave = async (
    modifiedFiles: Map<string, string>,
    allFiles: FilesEditor_FileFragment[],
  ) => {
    const fileInputs = Array.from(modifiedFiles.entries()).map(
      ([fileId, content]) => {
        const file = allFiles.find((f) => f.id === fileId);
        return {
          path: file?.path ?? fileId,
          content,
        };
      },
    );

    try {
      const { data } = await updateWebapp({
        variables: {
          input: {
            id: webappId,
            files: fileInputs,
          },
        },
        refetchQueries: ["WebappVersions"],
      });

      if (data?.updateWebapp?.success) {
        toast.success(t("Webapp saved successfully"));
        refetch().then();
        return { success: true };
      } else {
        const error = data?.updateWebapp?.errors?.[0] ?? "Save failed";
        return { success: false, error: String(error) };
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Save failed",
      };
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="md" />
      </div>
    );
  }

  return (
    <FilesEditor
      name={t("Webapp")}
      files={files}
      isEditable={isEditable}
      onSave={handleSave}
    />
  );
};

export default WebappFilesEditor;
