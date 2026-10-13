import {
  CheckIcon,
  ChevronDownIcon,
  GlobeAltIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { McpResource, WorkspaceMembershipRole } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useMemo, useState } from "react";
import Flag from "react-world-flags";

export type MCPTool = {
  name: string;
  description: string;
  resource?: McpResource | null;
  write: boolean;
};

export type MCPGrant = {
  workspaceSlugs: string[];
  tools: string[];
};

export type MCPWorkspace = {
  slug: string;
  name: string;
  countries: { code: string }[];
  currentMembership?: { role: WorkspaceMembershipRole } | null;
};

type Props = {
  grant: MCPGrant;
  workspaces: MCPWorkspace[];
  tools: MCPTool[];
  onChange: (grant: MCPGrant) => void;
  disabled?: boolean;
  idPrefix: string;
};

const SEARCHABLE_FROM = 8;

const RESOURCE_ORDER: McpResource[] = [
  McpResource.Workspaces,
  McpResource.Files,
  McpResource.Datasets,
  McpResource.Pipelines,
  McpResource.Templates,
  McpResource.Webapps,
  McpResource.Databases,
  McpResource.SavedQueries,
  McpResource.Connections,
];

const SelectAllLink = ({
  allSelected,
  disabled,
  onChange,
}: {
  allSelected: boolean;
  disabled?: boolean;
  onChange: (checked: boolean) => void;
}) => {
  const { t } = useTranslation();
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onChange(!allSelected)}
      className="text-sm text-blue-600 hover:underline disabled:text-gray-400 disabled:no-underline"
    >
      {allSelected ? t("Deselect all") : t("Select all")}
    </button>
  );
};

type AccessLevel = "NONE" | "READ" | "WRITE";

const LevelSelector = ({
  name,
  options,
  value,
  disabled,
  onChange,
}: {
  name: string;
  options: { level: AccessLevel; label: string; unavailable?: boolean }[];
  value: AccessLevel | null;
  disabled?: boolean;
  onChange: (level: AccessLevel) => void;
}) => (
  <div
    role="radiogroup"
    className="grid shrink-0 grid-cols-3 gap-0.5 rounded-lg border border-gray-200 bg-gray-50 p-0.5"
  >
    {options.map((option) => (
      <label
        key={option.level}
        className={clsx(
          "w-24 rounded-md px-2 py-1 text-center text-xs font-medium whitespace-nowrap transition-colors",
          value === option.level
            ? "bg-blue-600 text-white shadow-sm"
            : option.unavailable
              ? "text-gray-300"
              : "text-gray-600 hover:bg-white hover:text-gray-900",
          disabled || option.unavailable
            ? "cursor-not-allowed"
            : "cursor-pointer",
          disabled && "opacity-60",
        )}
      >
        <input
          type="radio"
          name={name}
          className="sr-only"
          checked={value === option.level}
          disabled={disabled || option.unavailable}
          onChange={() => onChange(option.level)}
        />
        {option.label}
      </label>
    ))}
  </div>
);

const MCPPermissionMatrix = ({
  grant,
  workspaces,
  tools,
  onChange,
  disabled = false,
  idPrefix,
}: Props) => {
  const { t } = useTranslation();
  const [workspaceQuery, setWorkspaceQuery] = useState("");
  const [expanded, setExpanded] = useState<Set<McpResource>>(new Set());

  const toggleExpanded = (resource: McpResource) => {
    const next = new Set(expanded);
    if (!next.delete(resource)) {
      next.add(resource);
    }
    setExpanded(next);
  };

  const matchingWorkspaces = useMemo(() => {
    const query = workspaceQuery.trim().toLowerCase();
    return query
      ? workspaces.filter((workspace) =>
          workspace.name.toLowerCase().includes(query),
        )
      : workspaces;
  }, [workspaces, workspaceQuery]);

  const groupLabels: Record<McpResource, string> = {
    [McpResource.Workspaces]: t("Workspaces"),
    [McpResource.Files]: t("Files"),
    [McpResource.Datasets]: t("Datasets"),
    [McpResource.Pipelines]: t("Pipelines"),
    [McpResource.Templates]: t("Pipeline templates"),
    [McpResource.Webapps]: t("Web apps"),
    [McpResource.Databases]: t("Databases"),
    [McpResource.SavedQueries]: t("Saved queries"),
    [McpResource.Connections]: t("Connections"),
  };

  const groupDescriptions: Record<McpResource, string> = {
    [McpResource.Workspaces]: t(
      "Let the assistant see your workspaces and change their settings.",
    ),
    [McpResource.Files]: t(
      "Let the assistant browse and read files in workspace buckets, and add new ones.",
    ),
    [McpResource.Datasets]: t(
      "Let the assistant list datasets, preview their contents, and publish new versions.",
    ),
    [McpResource.Pipelines]: t(
      "Let the assistant inspect pipelines and their runs, and create, edit or run them.",
    ),
    [McpResource.Templates]: t(
      "Let the assistant browse pipeline templates and read their source code.",
    ),
    [McpResource.Webapps]: t(
      "Let the assistant read web apps and edit the files they are built from.",
    ),
    [McpResource.Databases]: t(
      "Let the assistant read the structure of your workspace databases.",
    ),
    [McpResource.SavedQueries]: t(
      "Let the assistant read the saved SQL queries of the Data Studio, and save or edit them.",
    ),
    [McpResource.Connections]: t(
      "Let the assistant list the external connections a workspace holds.",
    ),
  };

  const toolsByGroup = useMemo(() => {
    const map = new Map<McpResource, MCPTool[]>();
    for (const tool of tools) {
      if (!tool.resource) {
        continue;
      }
      map.set(tool.resource, [...(map.get(tool.resource) ?? []), tool]);
    }
    return map;
  }, [tools]);

  const granted = useMemo(() => new Set(grant.tools), [grant.tools]);
  const viewerWorkspaceCount = workspaces.filter(
    (workspace) =>
      grant.workspaceSlugs.includes(workspace.slug) &&
      workspace.currentMembership?.role === WorkspaceMembershipRole.Viewer,
  ).length;
  const grantsWrite = tools.some(
    (tool) => tool.resource && tool.write && granted.has(tool.name),
  );

  const groups = RESOURCE_ORDER.filter(
    (resource) => (toolsByGroup.get(resource) ?? []).length > 0,
  );
  const hasWrite = (resource: McpResource) =>
    (toolsByGroup.get(resource) ?? []).some((tool) => tool.write);

  const setTools = (names: Set<string>) =>
    onChange({ ...grant, tools: Array.from(names).sort() });

  const levelOf = (groupTools: MCPTool[]): AccessLevel | null => {
    const selected = groupTools.filter((tool) => granted.has(tool.name));
    const reads = groupTools.filter((tool) => !tool.write);
    if (selected.length === 0) {
      return "NONE";
    }
    if (selected.length === groupTools.length) {
      return groupTools.some((tool) => tool.write) ? "WRITE" : "READ";
    }
    if (
      selected.length === reads.length &&
      selected.every((tool) => !tool.write)
    ) {
      return "READ";
    }
    return null;
  };

  const setLevel = (resources: McpResource[], level: AccessLevel) => {
    const next = new Set(granted);
    for (const resource of resources) {
      for (const tool of toolsByGroup.get(resource) ?? []) {
        const allowed = level === "WRITE" || (level === "READ" && !tool.write);
        if (allowed) {
          next.add(tool.name);
        } else {
          next.delete(tool.name);
        }
      }
    }
    setTools(next);
  };

  const overallLevel = (): AccessLevel | null => {
    const levels = groups.map((resource) => ({
      level: levelOf(toolsByGroup.get(resource) ?? []),
      canWrite: hasWrite(resource),
    }));
    if (levels.every(({ level }) => level === "NONE")) {
      return "NONE";
    }
    if (levels.every(({ level }) => level === "READ")) {
      return "READ";
    }
    if (
      levels.every(
        ({ level, canWrite }) =>
          level === "WRITE" || (level === "READ" && !canWrite),
      )
    ) {
      return "WRITE";
    }
    return null;
  };

  const levelOptions = (canWrite: boolean) => [
    {
      level: "WRITE" as const,
      label: t("Read & Write"),
      unavailable: !canWrite,
    },
    { level: "READ" as const, label: t("Read") },
    { level: "NONE" as const, label: t("No access") },
  ];

  const setWorkspaces = (slugs: Set<string>) =>
    onChange({ ...grant, workspaceSlugs: Array.from(slugs).sort() });

  const toggleWorkspace = (slug: string, checked: boolean) => {
    const next = new Set(grant.workspaceSlugs);
    if (checked) {
      next.add(slug);
    } else {
      next.delete(slug);
    }
    setWorkspaces(next);
  };

  return (
    <div className="space-y-6">
      <section className="space-y-3">
        <div className="flex items-baseline justify-between gap-4">
          <h5 className="font-medium text-gray-900">
            {t("Authorize access for")}
          </h5>
          <div className="flex items-baseline gap-4">
            <span className="text-sm text-gray-500">
              {t("{{count}} of {{total}} workspaces selected", {
                count: grant.workspaceSlugs.length,
                total: workspaces.length,
              })}
            </span>
            <SelectAllLink
              allSelected={
                workspaces.length > 0 &&
                grant.workspaceSlugs.length === workspaces.length
              }
              disabled={disabled || workspaces.length === 0}
              onChange={(checked) =>
                setWorkspaces(
                  new Set(
                    checked
                      ? workspaces.map((workspace) => workspace.slug)
                      : [],
                  ),
                )
              }
            />
          </div>
        </div>
        <div className="rounded-lg border border-gray-200 p-4">
          {workspaces.length > SEARCHABLE_FROM && (
            <input
              type="search"
              value={workspaceQuery}
              disabled={disabled}
              onChange={(event) => setWorkspaceQuery(event.target.value)}
              placeholder={t("Filter workspaces")}
              className="mb-3 w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm placeholder-gray-400 focus:border-gray-400 focus:ring-0 focus:outline-hidden"
            />
          )}
          <div className="grid max-h-72 grid-cols-1 overflow-y-auto sm:grid-cols-2">
            {matchingWorkspaces.map((workspace) => (
              <label
                key={workspace.slug}
                htmlFor={`${idPrefix}-workspace-${workspace.slug}`}
                className={clsx(
                  "flex items-center gap-2.5 rounded-md px-2 py-1.5",
                  disabled
                    ? "cursor-not-allowed"
                    : "cursor-pointer hover:bg-gray-50",
                )}
              >
                <input
                  type="checkbox"
                  id={`${idPrefix}-workspace-${workspace.slug}`}
                  disabled={disabled}
                  checked={grant.workspaceSlugs.includes(workspace.slug)}
                  onChange={(event) =>
                    toggleWorkspace(workspace.slug, event.target.checked)
                  }
                  className="form-checkbox h-4 w-4 shrink-0 cursor-pointer rounded-sm border-gray-300 text-blue-500 focus:ring-0 focus:ring-offset-0"
                />
                <span className="flex h-full w-5 shrink-0 items-center">
                  {workspace.countries.length === 1 ? (
                    <Flag
                      code={workspace.countries[0].code}
                      className="w-5 shrink rounded-xs"
                    />
                  ) : (
                    <GlobeAltIcon className="w-5 shrink rounded-xs text-gray-400" />
                  )}
                </span>
                <span className="min-w-0 flex-1">
                  <span
                    className="block truncate text-sm text-gray-900"
                    title={workspace.name}
                  >
                    {workspace.name}
                  </span>
                  <span className="block truncate font-mono text-xs text-gray-400">
                    {workspace.slug}
                  </span>
                </span>
                {workspace.currentMembership?.role ===
                  WorkspaceMembershipRole.Viewer && (
                  <span className="shrink-0 rounded bg-amber-50 px-1.5 py-0.5 text-xs font-medium text-amber-700">
                    {t("Viewer")}
                  </span>
                )}
              </label>
            ))}
          </div>
          {workspaces.length === 0 && (
            <p className="text-sm text-gray-500">
              {t("You are not a member of any workspace yet.")}
            </p>
          )}
          {workspaces.length > 0 && matchingWorkspaces.length === 0 && (
            <p className="text-sm text-gray-500">
              {t("No workspace matches that filter.")}
            </p>
          )}
        </div>
      </section>

      <section className="space-y-3">
        <h5 className="font-medium text-gray-900">{t("Permissions")}</h5>
        {viewerWorkspaceCount > 0 && grantsWrite && (
          <p className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
            {t(
              "You are a viewer in {{count}} of the selected workspaces: there, the assistant can only do what a viewer can, whatever you choose below.",
              { count: viewerWorkspaceCount },
            )}
          </p>
        )}

        <div className="divide-y divide-gray-200 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between gap-4 bg-gray-50 px-4 py-2.5">
            <p className="text-sm font-medium text-gray-900">
              {t("All resources")}
              {overallLevel() === null && (
                <span className="ml-2 text-xs font-normal text-gray-400">
                  {t("Custom")}
                </span>
              )}
            </p>
            <LevelSelector
              name={`${idPrefix}-level-all`}
              options={levelOptions(true)}
              value={overallLevel()}
              disabled={disabled}
              onChange={(level) => setLevel(groups, level)}
            />
          </div>
          {groups.map((resource) => {
            const level = levelOf(toolsByGroup.get(resource) ?? []);
            return (
              <div
                key={resource}
                className="flex items-start justify-between gap-4 px-4 py-3"
              >
                <div className="min-w-0">
                  <p className="text-sm text-gray-500">
                    <span className="font-medium text-gray-900">
                      {groupLabels[resource]}
                    </span>
                    {level === null && (
                      <span className="ml-2 text-xs text-gray-400">
                        {t("Custom")}
                      </span>
                    )}
                    <span className="ml-2">{groupDescriptions[resource]}</span>
                  </p>
                  <button
                    type="button"
                    aria-expanded={expanded.has(resource)}
                    onClick={() => toggleExpanded(resource)}
                    className="mt-1 inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
                  >
                    {expanded.has(resource) ? t("Hide tools") : t("Show tools")}
                    <ChevronDownIcon
                      className={clsx(
                        "h-3 w-3 transition-transform",
                        expanded.has(resource) && "rotate-180",
                      )}
                    />
                  </button>
                  {expanded.has(resource) && (
                    <ul className="mt-2 space-y-1">
                      {(toolsByGroup.get(resource) ?? []).map((tool) => (
                        <li
                          key={tool.name}
                          className="flex items-center gap-1.5 text-xs"
                        >
                          {granted.has(tool.name) ? (
                            <CheckIcon className="h-3.5 w-3.5 text-green-600" />
                          ) : (
                            <XMarkIcon className="h-3.5 w-3.5 text-gray-300" />
                          )}
                          <code
                            className={
                              granted.has(tool.name)
                                ? "text-gray-700"
                                : "text-gray-400"
                            }
                          >
                            {tool.name}
                          </code>
                          {tool.write && (
                            <span className="rounded bg-amber-50 px-1 text-[10px] font-medium text-amber-700">
                              {t("write")}
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <LevelSelector
                  name={`${idPrefix}-level-${resource}`}
                  options={levelOptions(hasWrite(resource))}
                  value={level}
                  disabled={disabled}
                  onChange={(next) => setLevel([resource], next)}
                />
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
};

export default MCPPermissionMatrix;
