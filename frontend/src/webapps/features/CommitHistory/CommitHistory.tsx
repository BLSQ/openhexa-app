import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import {
  useWebappVersionsQuery,
  WebappVersion_VersionFragment,
} from "webapps/graphql/queries.generated";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import Spinner from "core/components/Spinner";
import { DateTime } from "luxon";
import { useState } from "react";

type CommitHistoryProps = {
  webappId: string;
  workspaceSlug: string;
  webappSlug: string;
  isEditable: boolean;
};

const CommitHistory = ({
  webappId,
  workspaceSlug,
  webappSlug,
  isEditable,
}: CommitHistoryProps) => {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);

  const { data, loading, refetch } = useWebappVersionsQuery({
    variables: { workspaceSlug, webappSlug, page, perPage: 20 },
  });

  const [updateWebapp, { loading: publishing }] = useUpdateWebappMutation();

  const versions = data?.webapp?.versions?.items ?? [];
  const source = data?.webapp?.source;
  const publishedVersion =
    source?.__typename === "GitSource" ? source.publishedVersion : null;

  const handlePublish = async (versionId: string) => {
    const { data } = await updateWebapp({
      variables: {
        input: { id: webappId, publishedVersionId: versionId },
      },
    });

    if (data?.updateWebapp?.success) {
      toast.success(t("Version published successfully"));
      refetch().then();
    } else {
      toast.error(t("Failed to publish version"));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Spinner size="md" />
      </div>
    );
  }

  if (versions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        {t("No versions yet. Edit files and save to get started.")}
      </div>
    );
  }

  return (
    <div>
      <div className="divide-y divide-gray-200">
        {versions.map((version: WebappVersion_VersionFragment) => {
          const isPublished = version.id === publishedVersion;
          const shortId = version.id.substring(0, 7);
          const date = DateTime.fromISO(version.date);

          return (
            <div
              key={version.id}
              className="flex items-center justify-between py-3 px-1"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <code className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded font-mono">
                    {shortId}
                  </code>
                  <span className="text-sm text-gray-900 truncate">
                    {version.message}
                  </span>
                  {isPublished && (
                    <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                      {t("Published")}
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {version.authorName} &middot; {date.toRelative()}
                </div>
              </div>
              {isEditable && !isPublished && (
                <button
                  onClick={() => handlePublish(version.id)}
                  disabled={publishing}
                  className="ml-4 shrink-0 rounded-md border border-gray-300 px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  {t("Publish")}
                </button>
              )}
            </div>
          );
        })}
      </div>
      {page > 1 && (
        <div className="flex justify-center pt-4">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="mr-2 text-sm text-blue-600 hover:text-blue-800"
          >
            {t("Previous")}
          </button>
          <button
            onClick={() => setPage((p) => p + 1)}
            className="text-sm text-blue-600 hover:text-blue-800"
            disabled={versions.length < 20}
          >
            {t("Next")}
          </button>
        </div>
      )}
      {page === 1 && versions.length >= 20 && (
        <div className="flex justify-center pt-4">
          <button
            onClick={() => setPage((p) => p + 1)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {t("Load more")}
          </button>
        </div>
      )}
    </div>
  );
};

export default CommitHistory;
