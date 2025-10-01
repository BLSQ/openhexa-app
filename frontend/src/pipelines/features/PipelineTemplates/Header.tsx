import React from "react";
import SearchInput from "core/features/SearchInput";
import Listbox from "core/components/Listbox";
import ViewToggleButton from "core/components/ViewToggleButton";
import { PipelineFunctionalType } from "graphql/types";
import { formatPipelineFunctionalType } from "workspaces/helpers/pipelines";
import { useTranslation } from "next-i18next";

type Filter = {
  workspaceFilter: any;
  setWorkspaceFilter: (filter: any) => void;
  workspaceFilterOptions: any[];
};

type HeaderProps = {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  filter?: Filter;
  view: "grid" | "card";
  setView: (view: "grid" | "card") => void;
  showCard?: boolean;
  functionalTypeFilter?: PipelineFunctionalType | null;
  setFunctionalTypeFilter?: (filter: PipelineFunctionalType | null) => void;
};

const Header = ({
  searchQuery,
  setSearchQuery,
  filter,
  view,
  setView,
  showCard,
  functionalTypeFilter,
  setFunctionalTypeFilter,
}: HeaderProps) => {
  const { t } = useTranslation();

  const functionalTypeOptions = [
    { value: null, label: t("All types") },
    ...Object.values(PipelineFunctionalType).map(type => ({
      value: type,
      label: formatPipelineFunctionalType(type)
    }))
  ];

  return (
    <div className={"my-5 flex justify-between"}>
      <SearchInput
        onSubmit={(event) => event.preventDefault()}
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.target.value ?? "")}
        className="shadow-xs border-gray-50 w-96"
      />

      <div className={"flex gap-5"}>
        {setFunctionalTypeFilter && (
          <Listbox
            value={functionalTypeOptions.find(opt => opt.value === functionalTypeFilter)}
            onChange={(option) => setFunctionalTypeFilter(option?.value || null)}
            options={functionalTypeOptions}
            by="value"
            getOptionLabel={(option) => option.label}
            className={"min-w-48"}
          />
        )}
        {filter && (
          <Listbox
            value={filter.workspaceFilter}
            onChange={filter.setWorkspaceFilter}
            options={filter.workspaceFilterOptions}
            by="id"
            getOptionLabel={(option) => option.label}
            className={"min-w-72"}
          />
        )}
        {showCard && <ViewToggleButton view={view} setView={setView} />}
      </div>
    </div>
  );
};

export default Header;
