import React from "react";
import SearchInput from "core/features/SearchInput";
import TagFilter from "core/components/TagFilter";
import ViewToggleButton from "core/components/ViewToggleButton";
import { useTranslation } from "react-i18next";

type WorkspacesHeaderProps = {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  view: "grid" | "card";
  setView: (view: "grid" | "card") => void;
  availableTags?: string[] | null;
  tagsFilter: string[];
  setTagsFilter: (tags: string[]) => void;
};

const WorkspacesHeader = ({
  searchQuery,
  setSearchQuery,
  view,
  setView,
  availableTags,
  tagsFilter,
  setTagsFilter,
}: WorkspacesHeaderProps) => {
  const { t } = useTranslation();
  return (
    <div className="mb-5 flex justify-between">
      <SearchInput
        onSubmit={(event) => event.preventDefault()}
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.target.value ?? "")}
        className="shadow-xs border-gray-50 w-96"
        placeholder={t("Search workspaces...")}
      />

      <div className="flex items-center gap-5">
        <TagFilter
          tags={availableTags}
          value={tagsFilter}
          onChange={setTagsFilter}
        />
        <ViewToggleButton view={view} setView={setView} />
      </div>
    </div>
  );
};

export default WorkspacesHeader;
