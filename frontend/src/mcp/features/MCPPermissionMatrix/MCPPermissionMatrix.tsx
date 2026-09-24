import { ChevronDownIcon, GlobeAltIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Checkbox from "core/components/forms/Checkbox";
import { McpResource } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo, useRef, useState } from "react";
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
  McpResource.Connections,
];

const PresetLink = ({
  label,
  active,
  disabled,
  onClick,
}: {
  label: string;
  active: boolean;
  disabled?: boolean;
  onClick: () => void;
}) => (
  <button
    type="button"
    disabled={disabled}
    onClick={onClick}
    className={clsx(
      "text-sm disabled:text-gray-400 disabled:no-underline",
      active ? "font-medium text-gray-900" : "text-blue-600 hover:underline",
    )}
  >
    {label}
  </button>
);

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

function firstSentence(text: string) {
  const [sentence] = text.split(/(?<=\.)\s/);
  return sentence ?? text;
}

const TriStateCheckbox = ({
  id,
  checked,
  indeterminate,
  disabled,
  onChange,
}: {
  id: string;
  checked: boolean;
  indeterminate: boolean;
  disabled?: boolean;
  onChange: (checked: boolean) => void;
}) => {
  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.indeterminate = indeterminate;
    }
  }, [indeterminate]);

  return (
    <input
      ref={ref}
      id={id}
      type="checkbox"
      checked={checked}
      disabled={disabled}
      onChange={(event) => onChange(event.target.checked)}
      className="form-checkbox mt-0.5 h-4 w-4 cursor-pointer rounded-sm border-gray-300 text-blue-500 focus:ring-0 focus:ring-offset-0"
    />
  );
};

const MCPPermissionMatrix = ({
  grant,
  workspaces,
  tools,
  onChange,
  disabled = false,
  idPrefix,
}: Props) => {
  const { t } = useTranslation();
  const [collapsed, setCollapsed] = useState<Set<McpResource>>(
    () => new Set(RESOURCE_ORDER),
  );
  const [workspaceQuery, setWorkspaceQuery] = useState("");

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
  const grantable = tools.filter((tool) => tool.resource);
  const selectedCount = granted.size;
  const readOnlyTools = grantable
    .filter((tool) => !tool.write)
    .map((tool) => tool.name);
  const isReadOnly =
    granted.size === readOnlyTools.length &&
    readOnlyTools.every((name) => granted.has(name));

  const isSelected = (tool: MCPTool) => granted.has(tool.name);

  const setTools = (names: Set<string>) =>
    onChange({ ...grant, tools: Array.from(names).sort() });

  const toggleTool = (name: string, checked: boolean) => {
    const next = new Set(granted);
    if (checked) {
      next.add(name);
    } else {
      next.delete(name);
    }
    setTools(next);
  };

  const toggleGroup = (resource: McpResource, checked: boolean) => {
    const next = new Set(granted);
    for (const tool of toolsByGroup.get(resource) ?? []) {
      if (checked) {
        next.add(tool.name);
      } else {
        next.delete(tool.name);
      }
    }
    setTools(next);
  };

  const toggleCollapsed = (resource: McpResource) => {
    const next = new Set(collapsed);
    if (!next.delete(resource)) {
      next.add(resource);
    }
    setCollapsed(next);
  };

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
        <div className="flex items-baseline justify-between gap-4">
          <h5 className="font-medium text-gray-900">{t("Permissions")}</h5>
          <div className="flex items-baseline gap-4">
            <span className="text-sm text-gray-500">
              {t("{{selected}} of {{total}} tools selected", {
                selected: selectedCount,
                total: grantable.length,
              })}
            </span>
            <PresetLink
              label={t("Read only")}
              active={isReadOnly}
              disabled={disabled}
              onClick={() => setTools(new Set(readOnlyTools))}
            />
            <PresetLink
              label={t("Read & write")}
              active={selectedCount === grantable.length}
              disabled={disabled}
              onClick={() =>
                setTools(new Set(grantable.map((tool) => tool.name)))
              }
            />
            <PresetLink
              label={t("None")}
              active={selectedCount === 0}
              disabled={disabled}
              onClick={() => setTools(new Set())}
            />
          </div>
        </div>

        <div className="space-y-3">
          {RESOURCE_ORDER.map((resource) => {
            const groupTools = toolsByGroup.get(resource) ?? [];
            const selected = groupTools.filter(isSelected);
            const isCollapsed = collapsed.has(resource);
            return (
              <div
                key={resource}
                className="rounded-lg border border-gray-200 p-4 hover:border-gray-300"
              >
                <div className="flex items-start gap-3">
                  <TriStateCheckbox
                    id={`${idPrefix}-group-${resource}`}
                    checked={
                      groupTools.length > 0 &&
                      selected.length === groupTools.length
                    }
                    indeterminate={
                      selected.length > 0 && selected.length < groupTools.length
                    }
                    disabled={disabled}
                    onChange={(checked) => toggleGroup(resource, checked)}
                  />
                  <button
                    type="button"
                    aria-expanded={!isCollapsed}
                    onClick={() => toggleCollapsed(resource)}
                    className="flex flex-1 items-start justify-between gap-2 text-left"
                  >
                    <span>
                      <span className="text-sm font-medium text-gray-900">
                        {groupLabels[resource]}
                      </span>
                      <span className="mt-0.5 block text-sm text-gray-500">
                        {groupDescriptions[resource]}
                      </span>
                    </span>
                    <ChevronDownIcon
                      className={clsx(
                        "mt-0.5 h-4 w-4 shrink-0 text-gray-400 transition-transform",
                        isCollapsed && "-rotate-90",
                      )}
                    />
                  </button>
                </div>

                {!isCollapsed && (
                  <div className="mt-4 space-y-3 pl-7">
                    {groupTools.map((tool) => (
                      <Checkbox
                        key={tool.name}
                        id={`${idPrefix}-tool-${tool.name}`}
                        name={`${idPrefix}-tool-${tool.name}`}
                        label={<code className="text-xs">{tool.name}</code>}
                        description={firstSentence(tool.description)}
                        disabled={disabled}
                        checked={isSelected(tool)}
                        onChange={(event) =>
                          toggleTool(tool.name, event.target.checked)
                        }
                      />
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
};

export default MCPPermissionMatrix;
