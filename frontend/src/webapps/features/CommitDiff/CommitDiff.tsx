import { useTranslation } from "next-i18next";
import { DateTime } from "luxon";
import Link from "next/link";
import { html } from "diff2html";
import DOMPurify from "dompurify";
import { useWebappCommitDiffQuery } from "webapps/graphql/queries.generated";
import Spinner from "core/components/Spinner";
import Badge from "core/components/Badge";

type CommitDiffProps = {
  workspaceSlug: string;
  webappSlug: string;
  commitId: string;
};

const CommitDiff = ({ workspaceSlug, webappSlug, commitId }: CommitDiffProps) => {
  const { t } = useTranslation();

  const { data, loading } = useWebappCommitDiffQuery({
    variables: { workspaceSlug, webappSlug, ref: commitId },
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="sm" />
      </div>
    );
  }

  const webapp = data?.webapp;
  const diff = webapp?.commitDiff;
  const source = webapp?.source;
  const publishedVersionId =
    source?.__typename === "GitSource" ? source.publishedVersion : null;
  const isPublished = publishedVersionId === commitId;

  const diffHtml = diff?.rawDiff
    ? DOMPurify.sanitize(html(diff.rawDiff, { drawFileList: true, matching: "lines", outputFormat: "line-by-line" }))
    : null;

  return (
    <div className="space-y-4">
      {diff && (
        <div className="rounded-md border border-gray-200 bg-gray-50 px-4 py-3">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-gray-900">
                  {diff.message}
                </span>
                {isPublished && (
                  <Badge className="shrink-0 bg-green-50 text-green-700 ring-green-600/20">
                    {t("Published")}
                  </Badge>
                )}
              </div>
              <div className="mt-1 text-xs text-gray-500">
                {diff.authorName} &middot;{" "}
                {DateTime.fromISO(diff.date).toLocaleString(DateTime.DATETIME_MED)}
              </div>
              <div className="mt-1 font-mono text-xs text-gray-400">
                {commitId.substring(0, 7)}
              </div>
            </div>
            <Link
              href={`/workspaces/${encodeURIComponent(workspaceSlug)}/webapps/${encodeURIComponent(webappSlug)}/code?ref=${commitId}`}
              className="shrink-0 rounded border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 shadow-xs hover:bg-gray-50"
            >
              {t("Browse at this point")}
            </Link>
          </div>
        </div>
      )}

      {diffHtml ? (
        <div dangerouslySetInnerHTML={{ __html: diffHtml }} />
      ) : (
        <div className="py-8 text-center text-sm text-gray-500">
          {t("No changes in this commit.")}
        </div>
      )}
    </div>
  );
};

export default CommitDiff;
