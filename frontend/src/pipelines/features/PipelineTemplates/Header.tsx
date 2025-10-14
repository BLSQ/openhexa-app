import React from "react";
import SearchInput from "core/features/SearchInput";
import Listbox from "core/components/Listbox";
import ViewToggleButton from "core/components/ViewToggleButton";
import Popover from "core/components/Popover";
import Checkbox from "core/components/forms/Checkbox";
import { PipelineFunctionalType } from "graphql/types";
import { formatPipelineFunctionalType } from "workspaces/helpers/pipelines";
import { useTranslation } from "next-i18next";
import { TagIcon, XMarkIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";

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
  tagsFilter?: string[];
  setTagsFilter?: (tags: string[]) => void;
  templateTags?: string[];
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
  tagsFilter,
  setTagsFilter,
  templateTags,
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
      <div className="flex gap-3">
        <SearchInput
          onSubmit={(event) => event.preventDefault()}
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value ?? "")}
          className="shadow-xs border-gray-50 w-96"
        />
        {setTagsFilter && templateTags && templateTags.length > 0 && (
          <Popover
            trigger={
              <div className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 cursor-pointer">
                <TagIcon className="w-4 h-4 text-gray-600" />
                <span className="text-sm text-gray-700">{t("Tags")}</span>
                {tagsFilter && tagsFilter.length > 0 && (
                  <Badge className="bg-purple-100 text-purple-700 ring-purple-400/20">
                    {tagsFilter.length}
                  </Badge>
                )}
              </div>
            }
            placement="bottom-start"
          >
            <div className="w-64 max-h-80 overflow-y-auto">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-900">{t("Filter by tags")}</h3>
                {tagsFilter && tagsFilter.length > 0 && (
                  <button
                    onClick={() => setTagsFilter([])}
                    className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                  >
                    <XMarkIcon className="w-3 h-3" />
                    {t("Clear")}
                  </button>
                )}
              </div>
              <div className="space-y-2">
                {templateTags.map((tag) => {
                  const handleToggle = () => {
                    const isSelected = tagsFilter?.includes(tag) || false;
                    if (isSelected) {
                      setTagsFilter((tagsFilter || []).filter((t) => t !== tag));
                    } else {
                      setTagsFilter([...(tagsFilter || []), tag]);
                    }
                  };

                  return (
                    <div
                      key={tag}
                      className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
                      onClick={handleToggle}
                    >
                      <Checkbox
                        checked={tagsFilter?.includes(tag) || false}
                        onChange={handleToggle}
                      />
                      <span className="text-sm text-gray-700">{tag}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </Popover>
        )}
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
      </div>

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
