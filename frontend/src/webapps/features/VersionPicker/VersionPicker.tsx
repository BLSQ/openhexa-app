import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import {
  useWebappVersionsQuery,
  WebappVersion_VersionFragment,
} from "webapps/graphql/queries.generated";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import Spinner from "core/components/Spinner";
import Listbox from "core/components/Listbox/Listbox";
import { DateTime } from "luxon";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const PER_PAGE = 20;

type VersionPickerProps = {
  webappId: string;
  workspaceSlug: string;
  webappSlug: string;
  isEditable: boolean;
};

const VersionPicker = ({
  webappId,
  workspaceSlug,
  webappSlug,
  isEditable,
}: VersionPickerProps) => {
  const { t } = useTranslation();
  const [extraVersions, setExtraVersions] = useState<
    WebappVersion_VersionFragment[]
  >([]);
  const [hasMore, setHasMore] = useState(true);
  const pageRef = useRef(1);

  const { data, loading, refetch } = useWebappVersionsQuery({
    variables: { workspaceSlug, webappSlug, page: 1, perPage: PER_PAGE },
  });

  const firstPageVersions = useMemo(
    () => data?.webapp?.versions?.items ?? [],
    [data],
  );

  useEffect(() => {
    setExtraVersions([]);
    setHasMore(firstPageVersions.length >= PER_PAGE);
    pageRef.current = 1;
  }, [firstPageVersions]);

  const allVersions = useMemo(
    () => [...firstPageVersions, ...extraVersions],
    [firstPageVersions, extraVersions],
  );

  const relativeDates = useMemo(
    () =>
      Object.fromEntries(
        allVersions.map((v) => {
          const dt = DateTime.fromISO(v.date);
          const diffSeconds = -dt.diffNow("seconds").seconds;
          const relative = diffSeconds < 60 ? t("Just now") : dt.toRelative();
          return [v.id, relative];
        }),
      ),
    [allVersions, t],
  );

  const [updateWebapp] = useUpdateWebappMutation();

  const source = data?.webapp?.source;
  const publishedVersionId =
    source?.__typename === "GitSource" ? source.publishedVersion : null;

  const currentPublishedVersion = useMemo(
    () =>
      allVersions.find((v) => v.id === publishedVersionId) ?? allVersions[0],
    [allVersions, publishedVersionId],
  );

  const handlePublish = async (versionId: string) => {
    const { data } = await updateWebapp({
      variables: {
        input: { id: webappId, publishedVersionId: versionId },
      },
      refetchQueries: ["WebappVersions"],
    });

    if (data?.updateWebapp?.success) {
      toast.success(t("Version published successfully"));
    } else {
      toast.error(t("Failed to publish version"));
    }
  };

  const handleScrollBottom = useCallback(() => {
    if (!hasMore) return;
    const nextPage = pageRef.current + 1;
    pageRef.current = nextPage;
    refetch({
      workspaceSlug,
      webappSlug,
      page: nextPage,
      perPage: PER_PAGE,
    }).then(({ data: d }) => {
      const items = d?.webapp?.versions?.items ?? [];
      setExtraVersions((prev) => [...prev, ...items]);
      setHasMore(items.length >= PER_PAGE);
    });
  }, [hasMore, refetch, workspaceSlug, webappSlug]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-4">
        <Spinner size="sm" />
      </div>
    );
  }

  if (allVersions.length === 0) {
    return (
      <div className="py-4 text-center text-sm text-gray-500">
        {t("No versions yet. Edit files and save to get started.")}
      </div>
    );
  }

  return (
    <Listbox
      value={currentPublishedVersion}
      options={allVersions}
      by="id"
      onChange={(version: WebappVersion_VersionFragment) => {
        if (isEditable && version.id !== publishedVersionId) {
          handlePublish(version.id).then();
        }
      }}
      onScrollBottom={hasMore ? handleScrollBottom : undefined}
      getOptionLabel={(v: WebappVersion_VersionFragment) =>
        v ? `${v.id.slice(0, 7)} - ${v.message}` : ""
      }
      renderOption={(
        version: WebappVersion_VersionFragment,
        { focus }: { focus: boolean; selected: boolean },
      ) => {
        const isPublished = version.id === publishedVersionId;
        const shortId = version.id.substring(0, 7);
        return (
          <div className="flex w-full items-center justify-between">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <code
                  className={`rounded px-1.5 py-0.5 font-mono text-xs ${
                    focus
                      ? "bg-blue-400/30 text-white"
                      : "bg-gray-100 text-gray-500"
                  }`}
                >
                  {shortId}
                </code>
                <span className="truncate text-sm">{version.message}</span>
                {isPublished && (
                  <span className="inline-flex shrink-0 items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                    {t("Published")}
                  </span>
                )}
              </div>
              <div
                className={`mt-0.5 text-xs ${focus ? "text-blue-100" : "text-gray-500"}`}
              >
                {version.authorName} &middot; {relativeDates[version.id]}
              </div>
            </div>
          </div>
        );
      }}
    />
  );
};

export default VersionPicker;
