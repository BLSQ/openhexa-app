import {
  ArrowUturnLeftIcon,
  ClockIcon,
  CodeBracketIcon,
  Cog6ToothIcon,
  SparklesIcon,
  TableCellsIcon,
} from "@heroicons/react/24/outline";
import SavedQueryChatPanel, {
  SavedQueryConversation,
} from "assistant/features/SavedQueryChatPanel";
import clsx from "clsx";
import Button from "core/components/Button";
import DetailShell, {
  AssistantDock,
  BrowsingVersionBanner,
  DetailBadge,
  DetailHeader,
  DetailViewPane,
  Segment,
  SegmentedViewSwitcher,
  useAssistantDock,
} from "core/components/DetailShell";
import Spinner from "core/components/Spinner";
import SubscriptionLimitTooltip from "core/components/SubscriptionLimitTooltip";
import useCacheKey from "core/hooks/useCacheKey";
import { SavedQueryVisibility } from "graphql/types";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "react-toastify";
import DataStudioEditor from "workspaces/features/DataStudioEditor";
import { useSavedQueryVisibilityOption } from "workspaces/features/SavedQueries/savedQueryVisibility";
import { useSavedQueryMutations } from "workspaces/features/SavedQueries/useSavedQueryMutations";
import { WorkspaceSavedQueryPageQuery } from "workspaces/graphql/queries.generated";
import { dataStudioRoutes } from "workspaces/helpers/dataStudio";
import {
  useSavedQueryVersionContentQuery,
  useSavedQueryVersionsQuery,
} from "./SavedQueryDetail.generated";
import SavedQueryCommitDiff from "./SavedQueryCommitDiff";
import SavedQueryHistory from "./SavedQueryHistory";
import SavedQuerySettings from "./SavedQuerySettings";

const ASSISTANT_STORAGE_KEY = "saved-query-assistant";

type View = "query" | "history" | "settings";

export type SavedQueryDetail_SavedQuery = NonNullable<
  WorkspaceSavedQueryPageQuery["savedQueryBySlug"]
>;

type SavedQueryDetailProps = {
  workspaceSlug: string;
  savedQuery: SavedQueryDetail_SavedQuery;
  canCreate: boolean;
  showAssistant: boolean;
  aiBudgetLimitReached: boolean;
  onRefetch: () => void;
};

// The saved query page, laid out like the web app and pipeline detail pages:
// a header, a Query / History / Settings switcher and the AI assistant docked
// on the right. The Query view is the Data Studio editor itself.
const SavedQueryDetail = ({
  workspaceSlug,
  savedQuery,
  canCreate,
  showAssistant,
  aiBudgetLimitReached,
  onRefetch,
}: SavedQueryDetailProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const canEdit = savedQuery.permissions.update;
  const visibilityOption = useSavedQueryVisibilityOption(savedQuery.visibility);

  const [view, setView] = useState<View>("query");
  const [versionRef, setVersionRef] = useState<string | null>(null);
  const [diffVersionId, setDiffVersionId] = useState<string | null>(null);

  // The history and the "latest" meta are refetched whenever a saved query is
  // written anywhere: by the editor, the settings, a restore or the assistant.
  const clearSavedQueriesCache = useCacheKey("savedQueries");
  const [historyKey, setHistoryKey] = useState(0);
  useCacheKey("savedQueries", () => setHistoryKey((k) => k + 1));

  const { data: versionsData, refetch: refetchLatest } =
    useSavedQueryVersionsQuery({
      variables: { slug: savedQuery.slug, page: 1, perPage: 1 },
    });
  useEffect(() => {
    refetchLatest().then();
  }, [historyKey, refetchLatest]);
  const latestVersion = versionsData?.savedQueryBySlug?.versions?.items?.[0];

  const { data: versionContentData } = useSavedQueryVersionContentQuery({
    variables: { slug: savedQuery.slug, ref: versionRef ?? "" },
    skip: !versionRef,
  });
  const versionContent = versionRef
    ? (versionContentData?.savedQueryBySlug?.versionContent ?? null)
    : null;

  const browseVersion = useCallback((versionId: string) => {
    setDiffVersionId(null);
    setVersionRef(versionId);
    setView("query");
  }, []);

  const { update, updating } = useSavedQueryMutations();
  const handleRestore = async () => {
    if (!versionRef || versionContent === null || updating) return;
    const res = await update({ id: savedQuery.id, content: versionContent });
    if (res.ok) {
      toast.success(t("Version restored as the latest one"));
      setVersionRef(null);
      onRefetch();
    } else {
      toast.error(res.message);
    }
  };

  // ---- assistant ----
  const [conversations, setConversations] = useState<SavedQueryConversation[]>(
    [],
  );
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const seededRef = useRef(false);
  useEffect(() => {
    if (seededRef.current) return;
    seededRef.current = true;
    const convs = savedQuery.assistantConversations ?? [];
    setConversations(convs);
    setActiveConversationId(convs[0]?.id ?? null);
  }, [savedQuery.assistantConversations]);

  const { isOpen: isAssistantOpen, toggle: toggleAssistant } = useAssistantDock(
    ASSISTANT_STORAGE_KEY,
  );
  const assistantAvailable = showAssistant && canEdit;

  const handleVersionSaved = useCallback(() => {
    // The editor picks the new SQL up from the refetched query; the history
    // and the "latest" meta from the cache key.
    setVersionRef(null);
    onRefetch();
    clearSavedQueriesCache();
  }, [onRefetch, clearSavedQueriesCache]);

  const segments: Segment<View>[] = [
    { id: "query", label: t("Query"), icon: CodeBracketIcon },
    { id: "history", label: t("History"), icon: ClockIcon },
    { id: "settings", label: t("Settings"), icon: Cog6ToothIcon },
  ];

  return (
    <DetailShell>
      <DetailHeader
        icon={<TableCellsIcon className="h-5 w-5 text-gray-500" />}
        title={savedQuery.name}
        badges={
          <DetailBadge
            color={
              savedQuery.visibility === SavedQueryVisibility.Workspace
                ? "emerald"
                : "gray"
            }
            icon={<visibilityOption.Icon className="h-3 w-3" />}
          >
            {visibilityOption.label}
          </DetailBadge>
        }
        meta={[
          <code key="slug" className="font-mono text-gray-600">
            {savedQuery.slug}
          </code>,
          savedQuery.createdBy && (
            <span key="author" className="text-gray-500">
              {t("by {{name}}", { name: savedQuery.createdBy.displayName })}
            </span>
          ),
          latestVersion && (
            <span key="latest" className="text-gray-500">
              {t("Latest")}{" "}
              <code className="font-mono text-gray-700">
                {latestVersion.id.substring(0, 7)}
              </code>{" "}
              &middot; {DateTime.fromISO(latestVersion.date).toRelative()}
            </span>
          ),
          savedQuery.description && (
            <span
              key="description"
              className="max-w-md truncate text-gray-500"
              title={savedQuery.description}
            >
              {savedQuery.description}
            </span>
          ),
        ]}
      />

      <DetailShell.Body>
        <DetailShell.Main>
          <SegmentedViewSwitcher
            segments={segments}
            value={view}
            onChange={setView}
            actions={
              assistantAvailable &&
              !isAssistantOpen && (
                <div className="ml-auto flex-none">
                  <SubscriptionLimitTooltip
                    isLimitReached={aiBudgetLimitReached}
                    title={t("Monthly AI budget reached")}
                  >
                    <Button
                      onClick={toggleAssistant}
                      variant="secondary"
                      size="md"
                      disabled={aiBudgetLimitReached}
                      leadingIcon={<SparklesIcon className="h-4 w-4" />}
                    >
                      {t("AI Assistant")}
                    </Button>
                  </SubscriptionLimitTooltip>
                </div>
              )
            }
          />

          {/* The editor stays mounted behind the other views and behind a
              browsed version, so unsaved edits survive a look at the history. */}
          <div
            className={clsx(
              "min-h-0 flex-1 flex-col",
              view === "query" ? "flex" : "hidden",
            )}
          >
            {versionRef && (
              <BrowsingVersionBanner
                label={
                  <>
                    {t("Browsing version")}{" "}
                    <code className="font-mono text-amber-900">
                      {versionRef.substring(0, 7)}
                    </code>{" "}
                    &middot; {t("read-only")}
                  </>
                }
                actions={
                  canEdit &&
                  versionRef !== latestVersion?.id && (
                    <button
                      onClick={handleRestore}
                      disabled={updating || versionContent === null}
                      className="inline-flex items-center gap-1.5 rounded border border-amber-300 bg-white px-2.5 py-1 text-xs font-medium text-amber-900 hover:bg-amber-50 disabled:opacity-60"
                    >
                      {updating && <Spinner size="xs" />}
                      {updating ? t("Restoring...") : t("Restore this version")}
                    </button>
                  )
                }
                onBack={() => setVersionRef(null)}
              />
            )}
            <div className="min-h-0 flex-1 p-5">
              <div className="h-full min-h-0 overflow-hidden rounded-[10px] border border-gray-200">
                <div className={clsx("h-full", versionRef && "hidden")}>
                  <DataStudioEditor
                    workspaceSlug={workspaceSlug}
                    savedQuery={savedQuery}
                    canCreate={canCreate}
                    showQueryDetails={false}
                    flush
                    onSaved={onRefetch}
                  />
                </div>
                {versionRef &&
                  (versionContent === null ? (
                    <div className="flex h-full items-center justify-center">
                      <Spinner size="sm" />
                    </div>
                  ) : (
                    <DataStudioEditor
                      key={versionRef}
                      workspaceSlug={workspaceSlug}
                      savedQuery={{ ...savedQuery, content: versionContent }}
                      canCreate={false}
                      showQueryDetails={false}
                      readOnly
                      flush
                    />
                  ))}
              </div>
            </div>
          </div>

          {view === "history" && (
            <DetailViewPane className="px-5 py-4">
              {diffVersionId ? (
                <div className="space-y-4">
                  <button
                    onClick={() => setDiffVersionId(null)}
                    className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 hover:underline"
                  >
                    <ArrowUturnLeftIcon className="h-3.5 w-3.5" />
                    {t("Back to history")}
                  </button>
                  <SavedQueryCommitDiff
                    slug={savedQuery.slug}
                    versionId={diffVersionId}
                    onBrowse={browseVersion}
                  />
                </div>
              ) : (
                <SavedQueryHistory
                  key={historyKey}
                  slug={savedQuery.slug}
                  onSelectVersion={setDiffVersionId}
                  onBrowseVersion={browseVersion}
                />
              )}
            </DetailViewPane>
          )}

          {view === "settings" && (
            <DetailViewPane className="bg-gray-50 px-5 py-4">
              <SavedQuerySettings
                savedQuery={savedQuery}
                onSaved={onRefetch}
                onDeleted={() =>
                  router.push(dataStudioRoutes(workspaceSlug).queries)
                }
              />
            </DetailViewPane>
          )}
        </DetailShell.Main>

        {assistantAvailable && isAssistantOpen && (
          <AssistantDock storageKey={ASSISTANT_STORAGE_KEY}>
            <SavedQueryChatPanel
              workspaceSlug={workspaceSlug}
              savedQueryId={savedQuery.id}
              onVersionSaved={handleVersionSaved}
              conversations={conversations}
              activeConversationId={activeConversationId}
              onConversationChange={setActiveConversationId}
              onNewConversation={() => setActiveConversationId(null)}
              onConversationCreated={(conversation) => {
                setConversations((prev) => [conversation, ...prev]);
                setActiveConversationId(conversation.id);
              }}
              onConversationNameChange={(id, conversationName) =>
                setConversations((prev) =>
                  prev.map((c) =>
                    c.id === id ? { ...c, name: conversationName } : c,
                  ),
                )
              }
              flush
              onClose={toggleAssistant}
            />
          </AssistantDock>
        )}
      </DetailShell.Body>
    </DetailShell>
  );
};

export default SavedQueryDetail;
