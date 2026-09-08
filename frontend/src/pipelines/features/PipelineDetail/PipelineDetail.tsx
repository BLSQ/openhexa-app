import {
  ArrowUturnLeftIcon,
  BookOpenIcon,
  ClockIcon,
  CodeBracketIcon,
  Cog6ToothIcon,
  CommandLineIcon,
  DocumentTextIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  PlayIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import AssistantProposalBanner from "assistant/features/AssistantProposalBanner";
import PipelineEditChatPanel, {
  PipelineConversation,
} from "assistant/features/PipelineEditChatPanel";
import { useResolveAssistantProposalMutation } from "assistant/graphql/mutations.generated";
import Badge from "core/components/Badge";
import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import CollapsibleMarkdown from "core/components/CollapsibleMarkdown";
import DataCard from "core/components/DataCard";
import MarkdownProperty from "core/components/DataCard/MarkdownProperty";
import RenderProperty from "core/components/DataCard/RenderProperty";
import SelectProperty from "core/components/DataCard/SelectProperty";
import SwitchProperty from "core/components/DataCard/SwitchProperty";
import TagProperty from "core/components/DataCard/TagProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import DetailShell, {
  AssistantDock,
  BrowsingVersionBanner,
  DetailBadge,
  DetailHeader,
  DetailViewPane,
  Segment,
  SegmentedViewSwitcher,
  SettingsCard,
  useAssistantDock,
} from "core/components/DetailShell";
import Link from "core/components/Link";
import Listbox from "core/components/Listbox";
import MarkdownViewer from "core/components/MarkdownViewer";
import Spinner from "core/components/Spinner";
import SubscriptionLimitTooltip from "core/components/SubscriptionLimitTooltip";
import Switch from "core/components/Switch";
import Tooltip from "core/components/Tooltip";
import useCacheKey from "core/hooks/useCacheKey";
import { PipelineFunctionalType, PipelineType } from "graphql/types";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineHistory from "pipelines/features/PipelineHistory";
import PipelineRuns from "pipelines/features/PipelineRuns";
import PipelineVersionCard from "pipelines/features/PipelineVersionCard";
import PipelineVersionParametersTable from "pipelines/features/PipelineVersionParametersTable";
import UpgradePipelineFromTemplateDialog from "pipelines/features/UpgradePipelineFromTemplateDialog";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import CronProperty from "workspaces/features/CronProperty";
import { ProposedFile } from "workspaces/features/FilesEditor/FilesEditor";
import { PipelineFilesEditor } from "workspaces/features/FilesEditor/PipelineFilesEditor";
import GeneratePipelineWebhookUrlDialog from "workspaces/features/GeneratePipelineWebhookUrlDialog";
import PipelineRecipients from "workspaces/features/PipelineRecipients";
import PipelineVersionConfigDialog from "workspaces/features/PipelineVersionConfigDialog";
import {
  GetPipelineVersionFilesQuery,
  useGetPipelineVersionFilesLazyQuery,
  WorkspacePipelineHistoryQuery,
} from "workspaces/graphql/queries.generated";
import {
  formatPipelineFunctionalType,
  formatPipelineSource,
  getCronExpressionNextRun,
  updatePipeline,
} from "workspaces/helpers/pipelines";

const ASSISTANT_STORAGE_KEY = "pipeline-assistant";

type PipelineVersion = NonNullable<
  WorkspacePipelineHistoryQuery["pipeline"]
>["versions"]["items"][number];

type BrowsedVersion = NonNullable<
  GetPipelineVersionFilesQuery["pipelineVersion"]
>;

const VIEWS = ["overview", "runs", "code", "history", "settings"] as const;
type View = (typeof VIEWS)[number];

type PipelineDetailProps = {
  workspaceSlug: string;
  pipelineCode: string;
  pipeline: any;
  showAssistant: boolean;
  aiBudgetLimitReached: boolean;
  monthlyLimitExceeded: boolean;
  onRefetch: () => void;
};

const PipelineDetail = ({
  workspaceSlug,
  pipelineCode,
  pipeline,
  showAssistant,
  aiBudgetLimitReached,
  monthlyLimitExceeded,
  onRefetch,
}: PipelineDetailProps) => {
  const { t } = useTranslation();
  const router = useRouter();

  const isZipFile = pipeline.type === PipelineType.ZipFile;
  const canEditCode = Boolean(pipeline.permissions?.createVersion);
  const clearCache = useCacheKey(["pipelines"], onRefetch);

  const [versionRef, setVersionRef] = useState<BrowsedVersion | null>(null);
  const [selectedVersion, setSelectedVersion] =
    useState<PipelineVersion | null>(null);
  const [isVersionConfigDialogOpen, setVersionConfigDialogOpen] =
    useState(false);
  const [isGenerateWebhookUrlDialogOpen, setIsGenerateWebhookUrlDialogOpen] =
    useState(false);
  const [isUpgradeFromTemplateDialogOpen, setUpgradeFromTemplateDialogOpen] =
    useState(false);

  const segments: Segment<View>[] = useMemo(
    () => [
      { id: "overview", label: t("Overview"), icon: DocumentTextIcon },
      { id: "runs", label: t("Runs"), icon: PlayIcon },
      ...(isZipFile && pipeline.currentVersion
        ? [{ id: "code" as const, label: t("Code"), icon: CodeBracketIcon }]
        : []),
      ...(isZipFile
        ? [{ id: "history" as const, label: t("History"), icon: ClockIcon }]
        : []),
      { id: "settings", label: t("Settings"), icon: Cog6ToothIcon },
    ],
    [t, isZipFile, pipeline.currentVersion],
  );

  const requestedView = router.query.tab as View | undefined;
  const view = segments.some((segment) => segment.id === requestedView)
    ? requestedView!
    : "overview";

  const setView = useCallback(
    (next: View) => {
      router.push(
        { pathname: router.pathname, query: { ...router.query, tab: next } },
        undefined,
        { shallow: true },
      );
    },
    [router],
  );

  // ---- version browsing ----
  const [fetchVersionFiles, { data: versionFilesData, loading: filesLoading }] =
    useGetPipelineVersionFilesLazyQuery();

  const browseVersion = useCallback(
    (versionId: string) => {
      setSelectedVersion(null);
      fetchVersionFiles({ variables: { versionId } }).then(({ data }) => {
        setVersionRef(data?.pipelineVersion ?? null);
      });
      setView("code");
    },
    [fetchVersionFiles, setView],
  );

  const versionToShow = versionRef
    ? versionFilesData?.pipelineVersion
    : pipeline.currentVersion;

  // ---- assistant / proposals ----
  const [resolveProposal] = useResolveAssistantProposalMutation();
  const [proposedFiles, setProposedFiles] = useState<ProposedFile[] | null>(
    null,
  );
  const [proposedDeletedPaths, setProposedDeletedPaths] = useState<
    string[] | null
  >(null);
  const [proposedToolInvocationId, setProposedToolInvocationId] = useState<
    string | null
  >(null);

  const handleProposedFiles = useCallback(
    (
      files: ProposedFile[] | null,
      toolInvocationId?: string,
      deletedPaths?: string[],
    ) => {
      setProposedFiles(files);
      setProposedDeletedPaths(deletedPaths ?? null);
      if (toolInvocationId !== undefined) {
        setProposedToolInvocationId(toolInvocationId);
      } else if (files !== null) {
        // New SSE proposal: clear the stored ID until Apollo refetch provides it.
        setProposedToolInvocationId(null);
      }
      if (files) {
        // Proposals always apply to the latest version, never to a browsed one.
        setVersionRef(null);
        setSelectedVersion(null);
        setView("code");
      }
    },
    [setView],
  );

  const handleDismiss = useCallback(async () => {
    setProposedFiles(null);
    setProposedDeletedPaths(null);
    const idToDismiss = proposedToolInvocationId;
    setProposedToolInvocationId(null);
    if (idToDismiss) {
      await resolveProposal({ variables: { toolInvocationId: idToDismiss } });
    }
  }, [proposedToolInvocationId, resolveProposal]);

  const handleVersionCreated = useCallback(() => {
    setVersionRef(null);
    setProposedFiles(null);
    setProposedDeletedPaths(null);
    const idToResolve = proposedToolInvocationId;
    setProposedToolInvocationId(null);
    if (idToResolve) {
      resolveProposal({ variables: { toolInvocationId: idToResolve } });
    }
    onRefetch();
  }, [proposedToolInvocationId, resolveProposal, onRefetch]);

  const [conversations, setConversations] = useState<PipelineConversation[]>(
    [],
  );
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const seededRef = useRef(false);

  useEffect(() => {
    if (seededRef.current || !pipeline) return;
    seededRef.current = true;
    const convs = pipeline.assistantConversations ?? [];
    setConversations(convs);
    setActiveConversationId(convs[0]?.id ?? null);
  }, [pipeline?.id]);

  const { isOpen: isAssistantOpen, toggle: toggleAssistant } = useAssistantDock(
    ASSISTANT_STORAGE_KEY,
  );
  const assistantAvailable = showAssistant && isZipFile && canEditCode;

  // ---- settings ----
  const onSavePipeline = async (values: any) => {
    await updatePipeline(pipeline.id, {
      name: values.name,
      description: values.description,
      tags: values.tags?.map((tag: any) => tag.name) || [],
      functionalType: values.functionalType,
    });
  };

  const onSaveWebhook = async (values: any) => {
    await updatePipeline(pipeline.id, {
      webhookEnabled: values.webhookEnabled,
    });
  };

  const onSaveAutoUpdate = async (values: any) => {
    await updatePipeline(pipeline.id, {
      autoUpdateFromTemplate: values.autoUpdateFromTemplate,
    });
    clearCache();
  };

  const onSaveScheduling = async (values: any) => {
    const schedulingEnabled = values.enableScheduling;
    await updatePipeline(pipeline.id, {
      schedule: schedulingEnabled ? values.schedule : null,
      ...(schedulingEnabled && {
        scheduledPipelineVersionId: values.scheduledPipelineVersion?.id ?? null,
      }),
    });
  };

  const pipelineFunctionalTypeOptions = [
    { value: null, label: t("Not set") },
    ...Object.values(PipelineFunctionalType).map((type) => ({
      value: type,
      label: formatPipelineFunctionalType(type),
    })),
  ];

  const hasMissingConfiguration = useMemo(() => {
    if (!isZipFile || !pipeline.schedule) return false;
    const version =
      pipeline.scheduledPipelineVersion ?? pipeline.currentVersion;
    if (!version) return false;
    return version.parameters.some(
      (p: any) => p.required && !version.config?.[p.code],
    );
  }, [isZipFile, pipeline]);

  const versionItems = pipeline.versions?.items ?? [];
  const pinnedVersion = pipeline.scheduledPipelineVersion;
  const versionOptions =
    pinnedVersion && !versionItems.some((v: any) => v.id === pinnedVersion.id)
      ? [pinnedVersion, ...versionItems]
      : versionItems;

  const nextRun = pipeline.schedule
    ? getCronExpressionNextRun(pipeline.schedule)
    : null;

  return (
    <DetailShell>
      <DetailShell.Main>
        <DetailHeader
          icon={
            pipeline.type === PipelineType.Notebook ? (
              <BookOpenIcon className="h-6 w-6 text-gray-400" />
            ) : (
              <CommandLineIcon className="h-6 w-6 text-gray-400" />
            )
          }
          title={pipeline.name ?? t("Pipeline")}
          badges={
            <>
              <DetailBadge color="gray">
                {formatPipelineSource(pipeline.type, !!pipeline.sourceTemplate)}
              </DetailBadge>
              {pipeline.functionalType && (
                <DetailBadge color="indigo">
                  {formatPipelineFunctionalType(pipeline.functionalType)}
                </DetailBadge>
              )}
              {pipeline.schedule && (
                <DetailBadge
                  color="blue"
                  icon={<ClockIcon className="h-3 w-3" />}
                >
                  {t("Scheduled")}
                </DetailBadge>
              )}
            </>
          }
          meta={[
            <span
              key="code"
              className="inline-flex items-center gap-1.5 text-gray-500"
            >
              <Clipboard value={pipeline.code}>
                <code className="font-mono text-gray-700">{pipeline.code}</code>
              </Clipboard>
            </span>,
            pipeline.currentVersion && (
              <span className="text-gray-500">
                {t("Latest")}{" "}
                <code className="font-mono text-gray-700">
                  {pipeline.currentVersion.versionName}
                </code>{" "}
                &middot;{" "}
                {DateTime.fromISO(
                  pipeline.currentVersion.createdAt,
                ).toRelative()}
              </span>
            ),
            nextRun && (
              <span className="text-gray-500">
                {t("Next run")} {nextRun.formatted}
              </span>
            ),
          ]}
        />

        <SegmentedViewSwitcher
          segments={segments}
          value={view}
          onChange={setView}
          actions={
            assistantAvailable &&
            !isAssistantOpen &&
            view === "code" && (
              <div className="ml-auto flex-none">
                <SubscriptionLimitTooltip
                  isLimitReached={aiBudgetLimitReached}
                  title={t("Monthly AI budget reached")}
                >
                  <Button
                    onClick={toggleAssistant}
                    variant="secondary"
                    size="md"
                    leadingIcon={<SparklesIcon className="h-4 w-4" />}
                  >
                    {t("AI Assistant")}
                  </Button>
                </SubscriptionLimitTooltip>
              </div>
            )
          }
        />

        {view === "overview" && (
          <DetailViewPane className="bg-gray-50 px-5 py-4">
            <div className="mx-auto max-w-4xl space-y-4">
              <SettingsCard title={t("Description")}>
                {pipeline.description ? (
                  <MarkdownViewer sm markdown={pipeline.description} />
                ) : (
                  <p className="text-sm italic text-gray-500">
                    {t("This pipeline has no description.")}
                  </p>
                )}
              </SettingsCard>
            </div>
          </DetailViewPane>
        )}

        {view === "runs" && (
          <DetailViewPane className="px-5 py-4">
            <PipelineRuns
              workspaceSlug={workspaceSlug}
              pipelineCode={pipelineCode}
            />
          </DetailViewPane>
        )}

        {view === "code" && isZipFile && pipeline.currentVersion && (
          <div className="flex min-h-0 flex-1 flex-col">
            {versionRef && (
              <BrowsingVersionBanner
                label={
                  <>
                    {t("Browsing")}{" "}
                    <code className="font-mono text-amber-900">
                      {versionRef.versionName}
                    </code>{" "}
                    &middot; {t("read-only")}
                  </>
                }
                onBack={() => setVersionRef(null)}
              />
            )}
            {proposedFiles && (
              <AssistantProposalBanner
                label={t("Proposed version from AI assistant")}
                onDismiss={handleDismiss}
                className="mx-5 mt-4"
              />
            )}
            <div className="min-h-0 flex-1 p-5">
              <div className="relative h-full min-h-0 overflow-hidden rounded-[10px] border border-gray-200">
                {filesLoading && (
                  <div className="absolute inset-0 z-10 flex items-center justify-center backdrop-blur-xs">
                    <Spinner size="md" />
                  </div>
                )}
                {versionToShow && (
                  <PipelineFilesEditor
                    key={versionToShow.id}
                    name={versionToShow.versionName}
                    files={versionToShow.files}
                    isEditable={canEditCode && !versionRef}
                    proposedFiles={proposedFiles ?? undefined}
                    proposedDeletedPaths={proposedDeletedPaths ?? undefined}
                    workspaceSlug={workspaceSlug}
                    pipelineCode={pipelineCode}
                    pipelineId={pipeline.id}
                    flush
                    onVersionCreated={handleVersionCreated}
                  />
                )}
              </div>
            </div>
          </div>
        )}

        {view === "history" && isZipFile && (
          <DetailViewPane className="px-5 py-4">
            {selectedVersion ? (
              <div className="space-y-4">
                <button
                  onClick={() => setSelectedVersion(null)}
                  className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 hover:underline"
                >
                  <ArrowUturnLeftIcon className="h-3.5 w-3.5" />
                  {t("Back to history")}
                </button>
                <PipelineVersionCard version={selectedVersion} />
              </div>
            ) : (
              <PipelineHistory
                workspaceSlug={workspaceSlug}
                pipelineCode={pipelineCode}
                onSelectVersion={setSelectedVersion}
                onBrowseVersion={browseVersion}
              />
            )}
          </DetailViewPane>
        )}

        {view === "settings" && (
          <DetailViewPane className="bg-gray-50 px-5 py-4">
            <div className="mx-auto max-w-4xl space-y-4">
              <DataCard item={pipeline}>
                <DataCard.FormSection
                  title={t("Information")}
                  onSave={
                    pipeline.permissions.update ? onSavePipeline : undefined
                  }
                  collapsible={false}
                >
                  <TextProperty
                    id="name"
                    accessor="name"
                    label={t("Name")}
                    visible={(value, isEditing) => isEditing}
                  />
                  <MarkdownProperty
                    id="description"
                    label={t("Description")}
                    accessor="description"
                  />
                  <TextProperty
                    id="code"
                    accessor="code"
                    label={t("Code")}
                    help={t(
                      "This is the code used to identify this pipeline using the cli.",
                    )}
                    readonly
                  />
                  <RenderProperty
                    id="source"
                    label={t("Source")}
                    accessor="type"
                  >
                    {(property) => (
                      <Badge className="bg-gray-50 ring-gray-500/20">
                        {formatPipelineSource(
                          property.displayValue,
                          !!pipeline.sourceTemplate,
                        )}
                      </Badge>
                    )}
                  </RenderProperty>
                  <TagProperty
                    id="tags"
                    accessor="tags"
                    label={t("Tags")}
                    defaultValue={t("Not set")}
                  />
                  <RenderProperty
                    id="functionalType"
                    accessor="functionalType"
                    label={t("Type")}
                    help={t("The functional purpose of this pipeline")}
                  >
                    {(property, section) =>
                      section.isEdited ? (
                        <div className="w-50">
                          <Listbox
                            value={
                              pipelineFunctionalTypeOptions.find(
                                (opt) => opt.value === property.formValue,
                              ) || pipelineFunctionalTypeOptions[0]
                            }
                            options={pipelineFunctionalTypeOptions}
                            onChange={(option) =>
                              property.setValue(option.value)
                            }
                            getOptionLabel={(opt) => opt.label}
                            by="value"
                          />
                        </div>
                      ) : (
                        <span>
                          {property.displayValue
                            ? formatPipelineFunctionalType(
                                property.displayValue,
                              )
                            : t("Not set")}
                        </span>
                      )
                    }
                  </RenderProperty>
                  {pipeline.type === PipelineType.Notebook && (
                    <RenderProperty
                      id="notebookPath"
                      accessor="notebookPath"
                      label={t("Notebook path")}
                      readonly
                    >
                      {(property) => (
                        <div className="flex items-center gap-1.5 text-xs">
                          <Clipboard value={property.displayValue}>
                            <Link
                              customStyle="hover:opacity-80"
                              href={`/workspaces/${encodeURIComponent(
                                workspaceSlug,
                              )}/files/${property.displayValue
                                .split("/")
                                .slice(0, -1)
                                .join("/")}`}
                            >
                              <code>{property.displayValue}</code>
                            </Link>
                          </Clipboard>
                        </div>
                      )}
                    </RenderProperty>
                  )}
                </DataCard.FormSection>
              </DataCard>

              {isZipFile && pipeline.currentVersion && (
                <SettingsCard
                  title={t("Parameters")}
                  actions={
                    pipeline.permissions.update &&
                    pipeline.currentVersion.parameters.length > 0 && (
                      <Button
                        variant="white"
                        size="sm"
                        onClick={() => setVersionConfigDialogOpen(true)}
                      >
                        {t("Set default values")}
                      </Button>
                    )
                  }
                >
                  {pipeline.currentVersion.parameters.length > 0 ? (
                    <>
                      <div className="overflow-hidden rounded-md border border-gray-100">
                        <PipelineVersionParametersTable
                          version={pipeline.currentVersion}
                        />
                      </div>
                      <PipelineVersionConfigDialog
                        version={pipeline.currentVersion}
                        open={isVersionConfigDialogOpen}
                        onClose={() => setVersionConfigDialogOpen(false)}
                      />
                    </>
                  ) : (
                    <div className="text-sm italic text-gray-500">
                      {t("This pipeline has no parameters.")}
                    </div>
                  )}
                </SettingsCard>
              )}

              <DataCard item={pipeline}>
                <DataCard.FormSection
                  title={
                    <div className="flex items-center">
                      {t("Scheduling")}
                      {pipeline.permissions.update &&
                        hasMissingConfiguration && (
                          <Tooltip
                            className="flex items-center"
                            label={t(
                              "Missing configuration: set default parameters to fix the problem.",
                            )}
                          >
                            <ExclamationCircleIcon className="ml-1.5 inline-block h-5 w-5 text-yellow-500" />
                          </Tooltip>
                        )}
                    </div>
                  }
                  onSave={
                    pipeline.permissions.update && pipeline.permissions.schedule
                      ? onSaveScheduling
                      : undefined
                  }
                  collapsible={false}
                >
                  <SwitchProperty
                    id="enableScheduling"
                    label={t("Enabled")}
                    accessor={(item) => Boolean(item.schedule)}
                  />
                  <CronProperty
                    id="schedule"
                    accessor="schedule"
                    label={t("Schedule")}
                    help={t(
                      "The schedule value should follow the CRON syntax.",
                    )}
                    placeholder="0 15 * * *"
                    visible={(_, __, values) =>
                      Boolean(values.enableScheduling || pipeline.schedule)
                    }
                    required={(_, __, values) =>
                      Boolean(values.enableScheduling)
                    }
                  />
                  {isZipFile && (
                    <SelectProperty
                      id="scheduledPipelineVersion"
                      accessor="scheduledPipelineVersion"
                      label={t("Version")}
                      help={t(
                        "Choose which version to run on schedule. Leave empty to always run the latest version.",
                      )}
                      options={versionOptions}
                      nullable
                      defaultValue={t("Latest version")}
                      getOptionLabel={(v: any) => v.versionName}
                      visible={(_, __, values) =>
                        Boolean(values.enableScheduling || pipeline.schedule)
                      }
                    />
                  )}
                </DataCard.FormSection>
              </DataCard>

              <SettingsCard title={t("Notifications")}>
                <PipelineRecipients className="w-full" pipeline={pipeline} />
              </SettingsCard>

              <DataCard item={pipeline}>
                <DataCard.FormSection
                  title={
                    <div className="flex items-center">
                      {t("Webhook")}
                      <Tooltip
                        placement="top"
                        renderTrigger={(ref) => (
                          <span ref={ref} data-testid="help">
                            <InformationCircleIcon className="ml-1 h-3 w-3 cursor-pointer" />
                          </span>
                        )}
                        label={t(
                          "You can use a webhook to trigger this pipeline from an external system using a POST request.",
                        )}
                      />
                    </div>
                  }
                  onSave={
                    pipeline.permissions.update ? onSaveWebhook : undefined
                  }
                  collapsible={false}
                >
                  <RenderProperty
                    label={t("Enabled")}
                    id="webhookEnabled"
                    accessor="webhookEnabled"
                  >
                    {(property, section) => (
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={
                            section.isEdited
                              ? property.formValue
                              : property.displayValue
                          }
                          onChange={property.setValue}
                          disabled={!section.isEdited}
                        />
                        {section.isEdited && (
                          <span className="text-xs text-gray-500">
                            {t(
                              "Anyone with the URL will be able to trigger this pipeline",
                            )}
                          </span>
                        )}
                      </div>
                    )}
                  </RenderProperty>
                  <RenderProperty
                    visible={() => Boolean(pipeline.webhookUrl)}
                    readonly
                    id="webhookUrl"
                    label={t("URL")}
                    accessor="webhookUrl"
                  >
                    {(property, section) => (
                      <div className="flex items-center gap-2">
                        <code className="max-w-[100ch] overflow-x-hidden text-ellipsis text-xs">
                          {property.displayValue}
                        </code>
                        {!section.isEdited && (
                          <Clipboard value={property.displayValue} />
                        )}
                        {section.isEdited && (
                          <>
                            <Button
                              className="whitespace-nowrap"
                              variant="secondary"
                              size="sm"
                              onClick={() =>
                                setIsGenerateWebhookUrlDialogOpen(true)
                              }
                            >
                              {t("Generate a new URL")}
                            </Button>
                            <GeneratePipelineWebhookUrlDialog
                              onClose={() =>
                                setIsGenerateWebhookUrlDialogOpen(false)
                              }
                              pipeline={pipeline}
                              open={isGenerateWebhookUrlDialogOpen}
                            />
                          </>
                        )}
                      </div>
                    )}
                  </RenderProperty>
                </DataCard.FormSection>
              </DataCard>

              {(pipeline.template || pipeline.sourceTemplate) && (
                <DataCard item={pipeline}>
                  <DataCard.FormSection
                    title={t("Template Settings")}
                    onSave={
                      pipeline.permissions.update && pipeline.sourceTemplate
                        ? onSaveAutoUpdate
                        : undefined
                    }
                    collapsible={false}
                  >
                    {pipeline.template && (
                      <RenderProperty
                        id="template"
                        accessor="template.name"
                        label={t("Template")}
                        readonly
                      >
                        {(templateName) => (
                          <Link
                            href={`/workspaces/${encodeURIComponent(
                              workspaceSlug,
                            )}/templates/${pipeline.template?.code}`}
                          >
                            {templateName.displayValue}
                          </Link>
                        )}
                      </RenderProperty>
                    )}
                    {pipeline.sourceTemplate && (
                      <RenderProperty
                        id="source_template"
                        accessor="sourceTemplate.name"
                        label={t("Source Template")}
                        readonly
                      >
                        {(sourceTemplateName) => (
                          <div className="flex items-center gap-2">
                            <Link
                              href={`/workspaces/${encodeURIComponent(
                                workspaceSlug,
                              )}/templates/${pipeline.sourceTemplate?.code}`}
                            >
                              {sourceTemplateName.displayValue}
                            </Link>
                            {pipeline.hasNewTemplateVersions &&
                              pipeline.permissions.createVersion && (
                                <Button
                                  variant="secondary"
                                  size="sm"
                                  onClick={() =>
                                    setUpgradeFromTemplateDialogOpen(true)
                                  }
                                >
                                  {t("Upgrade to latest version")}
                                </Button>
                              )}
                          </div>
                        )}
                      </RenderProperty>
                    )}
                    {pipeline.sourceTemplate && (
                      <RenderProperty
                        label={t("Auto-update from template")}
                        id="autoUpdateFromTemplate"
                        accessor="autoUpdateFromTemplate"
                      >
                        {(property, section) => (
                          <div className="flex items-center gap-2">
                            <Switch
                              checked={
                                section.isEdited
                                  ? property.formValue
                                  : property.displayValue
                              }
                              onChange={property.setValue}
                              disabled={!section.isEdited}
                            />
                            {section.isEdited && (
                              <span className="text-xs text-gray-500">
                                {t(
                                  "When enabled, this pipeline will be automatically updated when new template versions are released",
                                )}
                              </span>
                            )}
                          </div>
                        )}
                      </RenderProperty>
                    )}
                    {pipeline.sourceTemplate && !pipeline.template && (
                      <RenderProperty
                        id="documentation"
                        accessor="sourceTemplate.documentation"
                        label={t("Template Documentation")}
                        readonly
                      >
                        {(property) => (
                          <CollapsibleMarkdown
                            content={property.displayValue}
                          />
                        )}
                      </RenderProperty>
                    )}
                  </DataCard.FormSection>
                </DataCard>
              )}
            </div>
          </DetailViewPane>
        )}
      </DetailShell.Main>

      {assistantAvailable && isAssistantOpen && view === "code" && (
        <AssistantDock storageKey={ASSISTANT_STORAGE_KEY}>
          <PipelineEditChatPanel
            pipelineId={pipeline.id}
            workspaceSlug={workspaceSlug}
            monthlyLimitExceeded={monthlyLimitExceeded}
            onProposedFiles={handleProposedFiles}
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

      <UpgradePipelineFromTemplateDialog
        pipeline={pipeline}
        open={isUpgradeFromTemplateDialogOpen}
        onClose={() => setUpgradeFromTemplateDialogOpen(false)}
        onSuccess={clearCache}
      />
    </DetailShell>
  );
};

export default PipelineDetail;
