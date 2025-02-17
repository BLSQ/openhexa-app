import React from "react";
import SearchInput from "core/features/SearchInput";
import Listbox from "core/components/Listbox";
import ViewToggleButton from "./ViewToggleButton";

type HeaderProps = {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  searchInputRef: React.RefObject<HTMLInputElement>;
  workspaceFilter: any;
  setWorkspaceFilter: (filter: any) => void;
  workspaceFilterOptions: any[];
  view: "grid" | "card";
  setView: (view: "grid" | "card") => void;
  showCard: boolean;
};

const Header = ({
  searchQuery,
  setSearchQuery,
  searchInputRef,
  workspaceFilter,
  setWorkspaceFilter,
  workspaceFilterOptions,
  view,
  setView,
  showCard,
}: HeaderProps) => {
  return (
    <div className={"my-5 flex justify-between"}>
      <SearchInput
        ref={searchInputRef}
        onSubmit={(event) => event.preventDefault()}
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.target.value ?? "")}
        className="shadow-xs border-gray-50 w-96"
      />
      <div className={"flex gap-5"}>
        <Listbox
          value={workspaceFilter}
          onChange={setWorkspaceFilter}
          options={workspaceFilterOptions}
          by="id"
          getOptionLabel={(option) => option.label}
          className={"min-w-72"}
        />
        {showCard && <ViewToggleButton view={view} setView={setView} />}
      </div>
    </div>
  );
};

export default Header;
