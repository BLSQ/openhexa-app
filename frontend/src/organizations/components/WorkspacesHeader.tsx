import React from "react";
import SearchInput from "core/features/SearchInput";
import ViewToggleButton from "core/components/ViewToggleButton";

type WorkspacesHeaderProps = {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  view: "grid" | "card";
  setView: (view: "grid" | "card") => void;
};

const WorkspacesHeader = ({
  searchQuery,
  setSearchQuery,
  view,
  setView,
}: WorkspacesHeaderProps) => {
  return (
    <div className="my-5 flex justify-between">
      <SearchInput
        onSubmit={(event) => event.preventDefault()}
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.target.value ?? "")}
        className="shadow-xs border-gray-50 w-96"
      />

      <div className="flex gap-5">
        <ViewToggleButton view={view} setView={setView} />
      </div>
    </div>
  );
};

export default WorkspacesHeader;
