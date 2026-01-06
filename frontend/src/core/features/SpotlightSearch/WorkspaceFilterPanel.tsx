import React, { useMemo, useState } from "react";
import MultiCombobox from "core/components/forms/Combobox/MultiCombobox";
import { Combobox } from "core/components/forms/Combobox";
import WorkspaceDisplay from "./WorkspaceDisplay";
import { GetWorkspacesQuery } from "./SpotlightSearch.generated";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button";
import clsx from "clsx";

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

  return (
    <div
      className="bg-white p-4"
      onKeyDown={(e) => e.stopPropagation()}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="flex justify-between items-center mb-3">
        <p className="text-sm font-medium">{t("Filter by Workspace")}</p>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="white"
            disabled={selectedWorkspaces.length >= workspaces.length}
            onClick={() => onChange(workspaces)}
          >
            {t("Select All")}
          </Button>
          <Button
            size="sm"
            variant="white"
            disabled={selectedWorkspaces.length === 0}
            onClick={() => onChange([])}
          >
            {t("Clear All")}
          </Button>
        </div>
      </div>
      <MultiCombobox
        onInputChange={(event) => setWorkspaceFilter(event.target.value)}
        displayValue={(workspace) => <WorkspaceDisplay workspace={workspace} />}
        value={selectedWorkspaces}
        onChange={onChange}
        className="z-40"
        maxDisplayedValues={5}
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
    </div>
  );
};

export default WorkspaceFilterPanel;
