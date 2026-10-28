import { useTranslation } from "next-i18next";
import { DateTime } from "luxon";
import { html } from "diff2html";
import DOMPurify from "dompurify";
import Spinner from "core/components/Spinner";
import { useSavedQueryCommitDiffQuery } from "./SavedQueryDetail.generated";

type SavedQueryCommitDiffProps = {
  slug: string;
  versionId: string;
  onBrowse: (versionId: string) => void;
};

// What one version changed in the SQL, rendered from the commit's diff.
const SavedQueryCommitDiff = ({
  slug,
  versionId,
  onBrowse,
}: SavedQueryCommitDiffProps) => {
  const { t } = useTranslation();

  const { data, loading } = useSavedQueryCommitDiffQuery({
    variables: { slug, ref: versionId },
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="sm" />
      </div>
    );
  }

  const diff = data?.savedQueryBySlug?.commitDiff;
  // A single-file repository: the file list would only ever name query.sql.
  const diffHtml = diff?.rawDiff
    ? DOMPurify.sanitize(
        html(diff.rawDiff, {
          drawFileList: false,
          matching: "lines",
          outputFormat: "line-by-line",
        }),
      )
    : null;

  return (
    <div className="space-y-4">
      {diff && (
        <div className="rounded-md border border-gray-200 bg-gray-50 px-4 py-3">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="text-sm font-semibold text-gray-900">
                {diff.message}
              </div>
              <div className="mt-1 text-xs text-gray-500">
                {diff.authorName} &middot;{" "}
                {DateTime.fromISO(diff.date).toLocaleString(
                  DateTime.DATETIME_MED,
                )}
              </div>
              <div className="mt-1 font-mono text-xs text-gray-400">
                {versionId.substring(0, 7)}
              </div>
            </div>
            <button
              onClick={() => onBrowse(versionId)}
              className="shrink-0 rounded border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 shadow-xs hover:bg-gray-50"
            >
              {t("Open this version in the editor")}
            </button>
          </div>
        </div>
      )}

      {diffHtml ? (
        <div dangerouslySetInnerHTML={{ __html: diffHtml }} />
      ) : (
        <div className="py-8 text-center text-sm text-gray-500">
          {t("No changes in this version.")}
        </div>
      )}
    </div>
  );
};

export default SavedQueryCommitDiff;
