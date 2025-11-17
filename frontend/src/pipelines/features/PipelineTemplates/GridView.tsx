import React, { useState, useMemo } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { SortingRule } from "react-table";
import DateColumn from "core/components/DataGrid/DateColumn";
import Block from "core/components/Block";
import Button from "core/components/Button";
import { useTranslation } from "next-i18next";
import { PlusIcon, TrashIcon } from "@heroicons/react/24/outline";
import Link from "core/components/Link";
import DeleteTemplateDialog from "pipelines/features/DeleteTemplateDialog";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { TagsCell, FunctionalTypeCell } from "pipelines/features/PipelineMetadataGrid";
import {
  GetPipelineTemplatesQuery,
  PipelineTemplates_WorkspaceFragment,
} from "./PipelineTemplates.generated";
import { PipelineTemplateOrderBy } from "graphql/types";
import { templateSorting } from "pipelines/config/sorting";
import TemplateBadge from "pipelines/features/TemplateBadge";

type PipelineTemplateItem = GetPipelineTemplatesQuery['pipelineTemplates']['items'][number];

type GridViewProps = {
  items: PipelineTemplateItem[];
  workspace: PipelineTemplates_WorkspaceFragment;
  page: number;
  perPage: number;
  totalItems: number;
  createPipeline: (pipelineTemplateVersionId: string) => () => void;
  setPage: (page: number) => void;
  onSort?: (params: {
    page: number;
    pageSize: number;
    pageIndex: number;
    sortBy: SortingRule<object>[];
  }) => void;
  currentSort?: PipelineTemplateOrderBy;
};

const GridView = ({
  items,
  workspace,
  perPage,
  totalItems,
  createPipeline,
  setPage,
  onSort,
  currentSort,
}: GridViewProps) => {
  const { t } = useTranslation();
  const [templateToDelete, setTemplateToDelete] = useState<PipelineTemplateItem | null>(null);

  const defaultSortBy = useMemo(
    () => templateSorting.convertToDataGridSort(currentSort),
    [currentSort]
  );

  return (
    <Block className="divide divide-y divide-gray-100 mt-4">
      <DataGrid
        key={currentSort}
        data={items}
        defaultPageSize={perPage}
        totalItems={totalItems}
        fetchData={onSort || (({ page }) => setPage(page))}
        sortable={Boolean(onSort)}
        defaultSortBy={defaultSortBy}
        fixedLayout={false}
      >
        <BaseColumn id="name" label={t("Name")}>
          {(template) => (
            <Link
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/templates/${template.code}`}
            >
              {template.name}
            </Link>
          )}
        </BaseColumn>
        <BaseColumn id="publisher" label={t("Publisher")} className="w-40" disableSortBy={true}>
          {(template) => (
            <TemplateBadge organization={template.organization} size="sm" />
          )}
        </BaseColumn>
        <BaseColumn id="version" label={t("Version")} className="w-20" disableSortBy={true}>
          {({ currentVersion }) => (
            <span className="text-sm">
              {currentVersion ? `v${currentVersion.versionNumber}` : "-"}
            </span>
          )}
        </BaseColumn>
        <TextColumn
          id="workspace"
          label={t("Workspace")}
          accessor="workspace.name"
          className="w-36"
          disableSortBy={true}
        />
        <BaseColumn id="tags" label={t("Tags")} className="w-32" disableSortBy={true}>
          {(template) => (
            <TagsCell tags={template.tags} maxTags={2} />
          )}
        </BaseColumn>
        <BaseColumn id="functionalType" label={t("Type")} className="w-28" disableSortBy={true}>
          {(template) => (
            <FunctionalTypeCell functionalType={template.functionalType} />
          )}
        </BaseColumn>
        <BaseColumn id="popularity" label={t("Popularity")} className="w-24">
          {(template) => (
            <span className="text-sm text-gray-600">
              {template.pipelinesCount > 0 ? (
                template.pipelinesCount
              ) : (
                <span className="text-gray-500 italic">{t("Not used")}</span>
              )}
            </span>
          )}
        </BaseColumn>
        <DateColumn
          id="createdAt"
          accessor={"currentVersion.createdAt"}
          label={t("Updated")}
          className="w-32"
        />
        <BaseColumn id="actions" className="text-right w-52" disableSortBy={true}>
          {(template) => {
            const {
              permissions: { delete: canDelete },
              currentVersion,
            } = template;
            return (
              <div className="flex justify-end gap-1">
                {currentVersion && (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={createPipeline(currentVersion.id)}
                    leadingIcon={<PlusIcon className="h-4 w-4" />}
                  >
                    {t("Create pipeline")}
                  </Button>
                )}
                {canDelete && (
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => setTemplateToDelete(template)}
                    leadingIcon={<TrashIcon className="h-4 w-4" />}
                  >
                    {t("Delete")}
                  </Button>
                )}
              </div>
            );
          }}
        </BaseColumn>
      </DataGrid>
      {templateToDelete && (
        <DeleteTemplateDialog
          open={true}
          pipelineTemplate={templateToDelete}
          onClose={() => setTemplateToDelete(null)}
        />
      )}
    </Block>
  );
};

export default GridView;
