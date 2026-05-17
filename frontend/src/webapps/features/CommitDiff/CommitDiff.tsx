import { useTranslation } from "next-i18next";
import { DateTime } from "luxon";
import Link from "next/link";
import { useWebappCommitDiffQuery } from "webapps/graphql/queries.generated";
import Spinner from "core/components/Spinner";
import Badge from "core/components/Badge";

type CommitDiffProps = {
  workspaceSlug: string;
  webappSlug: string;
  commitId: string;
};

type DiffLine = {
  type: "addition" | "deletion" | "context" | "hunk";
  content: string;
};

function parsePatch(patch: string): DiffLine[] {
  return patch.split("\n").map((line) => {
    if (line.startsWith("@@")) return { type: "hunk", content: line };
    if (line.startsWith("+")) return { type: "addition", content: line };
    if (line.startsWith("-")) return { type: "deletion", content: line };
    return { type: "context", content: line };
  });
}

const lineClasses: Record<DiffLine["type"], string> = {
  addition: "bg-green-50 text-green-800",
  deletion: "bg-red-50 text-red-800",
  hunk: "bg-blue-50 text-blue-700 font-mono text-xs",
  context: "text-gray-700",
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
  const files = diff?.files ?? [];
  const source = webapp?.source;
  const publishedVersionId =
    source?.__typename === "GitSource" ? source.publishedVersion : null;
  const isPublished = publishedVersionId === commitId;

  const totalAdditions = diff?.totalAdditions ?? 0;
  const totalDeletions = diff?.totalDeletions ?? 0;

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
                {DateTime.fromISO(diff.date).toLocaleString(
                  DateTime.DATETIME_MED,
                )}
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

      {files.length === 0 ? (
        <div className="py-8 text-center text-sm text-gray-500">
          {t("No changes in this commit.")}
        </div>
      ) : (
        <>
          <div className="text-sm text-gray-500">
            {files.length} {t("files changed")},{" "}
            <span className="text-green-700">+{totalAdditions}</span>{" "}
            <span className="text-red-700">-{totalDeletions}</span>
          </div>
          <div className="space-y-4">
            {files.map((file) => {
              const lines = file.patch ? parsePatch(file.patch) : [];
              const displayName =
                file.status === "renamed"
                  ? `${file.previousFilename} → ${file.filename}`
                  : file.filename;
              return (
                <div
                  key={file.filename}
                  className="overflow-hidden rounded-md border border-gray-200"
                >
                  <div className="flex items-center justify-between gap-4 border-b border-gray-200 bg-gray-50 px-3 py-2">
                    <span className="font-mono text-sm font-medium text-gray-800">
                      {displayName}
                    </span>
                    <span className="shrink-0 text-xs text-gray-500">
                      <span className="text-green-700">+{file.additions}</span>{" "}
                      <span className="text-red-700">-{file.deletions}</span>
                    </span>
                  </div>
                  {lines.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse font-mono text-xs">
                        <tbody>
                          {lines.map((line, i) => (
                            <tr
                              key={i}
                              className={lineClasses[line.type]}
                            >
                              <td className="select-none whitespace-pre px-3 py-0.5 text-right text-gray-400 align-top">
                                {line.type !== "hunk" ? i + 1 : ""}
                              </td>
                              <td className="whitespace-pre px-3 py-0.5 align-top">
                                {line.content}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="px-3 py-4 text-center text-xs text-gray-400">
                      {t("Binary file or no diff available")}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default CommitDiff;
