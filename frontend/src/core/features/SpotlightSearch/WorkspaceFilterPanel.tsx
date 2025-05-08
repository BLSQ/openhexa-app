import React, { useMemo, useState } from "react";
import clsx from "clsx";
import MultiCombobox from "core/components/forms/Combobox/MultiCombobox";
import { Combobox } from "core/components/forms/Combobox";
import WorkspaceDisplay from "./WorkspaceDisplay";
import { GetWorkspacesQuery } from "./SpotlightSearch.generated";
import { useTranslation } from "next-i18next";

type Workspace = GetWorkspacesQuery["workspaces"]["items"][0];

type WorkspaceFilterPanelProps = {
  workspaces: Workspace[];
  selectedWorkspaces: Workspace[];
  onChange: (selected: Workspace[]) => void;
};

const WorkspaceFilterPanel = ({
  workspaces,
  selectedWorkspaces,
  onChange,
}: WorkspaceFilterPanelProps) => {
  const [workspaceFilter, setWorkspaceFilter] = useState<string>("");
  const { t } = useTranslation();

  const filteredWorkspaces = useMemo(
    () =>
      workspaces.filter((item) =>
        item.name.toLowerCase().includes(workspaceFilter.toLowerCase()),
      ),
    [workspaces, workspaceFilter],
  );

  const selectedWorkspaceSlugs = useMemo(
    () => selectedWorkspaces.map((workspace) => workspace.slug),
    [selectedWorkspaces],
  );

  const toggleWorkspaceSelection = (workspace: Workspace) => {
    onChange(
      selectedWorkspaceSlugs.includes(workspace.slug)
        ? selectedWorkspaces.filter((ws) => ws.slug !== workspace.slug)
        : [...selectedWorkspaces, workspace],
    );
  };

  return (
    <div className="bg-white p-4">
      <p className="text-md font-medium mb-5">{t("Filter by Workspace")}</p>
      {workspaces.length <= 10 ? (
        <div className="flex gap-2 flex-wrap">
          {workspaces.map((workspace) => (
            <button
              key={workspace.slug}
              onClick={() => toggleWorkspaceSelection(workspace)}
              className={clsx(
                "px-3 py-1 rounded-full text-sm font-medium border hover:scale-105 cursor-pointer",
                selectedWorkspaceSlugs.includes(workspace.slug)
                  ? "bg-blue-400 text-white border-blue-400"
                  : "bg-gray-100 text-gray-700 border-gray-200",
              )}
            >
              <WorkspaceDisplay workspace={workspace} />
            </button>
          ))}
        </div>
      ) : (
        <MultiCombobox
          onInputChange={(event) => setWorkspaceFilter(event.target.value)}
          displayValue={(workspace) => (
            <WorkspaceDisplay workspace={workspace} />
          )}
          value={selectedWorkspaces}
          onChange={onChange}
          className="z-40"
        >
          {filteredWorkspaces.length > 0 ? (
            filteredWorkspaces.map((workspace) => (
              <Combobox.CheckOption
                key={workspace.slug}
                value={workspace}
                className={clsx(
                  selectedWorkspaceSlugs.includes(workspace.slug)
                    ? "bg-blue-400 text-white"
                    : "",
                )}
              >
                {workspace.name}
              </Combobox.CheckOption>
            ))
          ) : (
            <div className="align-middle px-3 py-2 text-sm text-gray-500">
              {t("No workspaces found")}
            </div>
          )}
        </MultiCombobox>
      )}
    </div>
  );
};

export default WorkspaceFilterPanel;
