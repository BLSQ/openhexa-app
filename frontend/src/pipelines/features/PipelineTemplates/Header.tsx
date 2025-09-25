import React from "react";
import SearchInput from "core/features/SearchInput";
import Listbox from "core/components/Listbox";
import ViewToggleButton from "../../../core/components/ViewToggleButton";

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
};

const Header = ({
  searchQuery,
  setSearchQuery,
  filter,
  view,
  setView,
  showCard,
}: HeaderProps) => {
  return (
    <div className={"my-5 flex justify-between"}>
      <SearchInput
        onSubmit={(event) => event.preventDefault()}
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.target.value ?? "")}
        className="shadow-xs border-gray-50 w-96"
      />

      <div className={"flex gap-5"}>
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
