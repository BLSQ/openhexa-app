import React, { useState } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import Block from "core/components/Block";
import Button from "core/components/Button";
import { useTranslation } from "next-i18next";
import { PlusIcon, TrashIcon } from "@heroicons/react/24/outline";
import Link from "core/components/Link";
import DeleteTemplateDialog from "pipelines/features/DeleteTemplateDialog";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Tag from "core/features/Tag";
import { formatPipelineFunctionalType } from "workspaces/helpers/pipelines";

type GridViewProps = {
  items: any[];
  workspace: any;
  page: number;
  perPage: number;
  totalItems: number;
  createPipeline: (pipelineTemplateVersionId: string) => () => void;
  setPage: (page: number) => void;
};

const GridView = ({
  items,
  workspace,
  perPage,
  totalItems,
  createPipeline,
  setPage,
}: GridViewProps) => {
  const { t } = useTranslation();
  const [templateToDelete, setTemplateToDelete] = useState<any | null>(null);

  return (
    <Block className="divide divide-y divide-gray-100 mt-4">
      <DataGrid
        data={items}
        defaultPageSize={perPage}
        totalItems={totalItems}
        fetchData={({ page }) => setPage(page)}
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
        <BaseColumn id="version" label={t("Version")} className="w-20">
          {({ currentVersion }) => (
            <span className="text-sm">
              {currentVersion ? `v${currentVersion.versionNumber}` : "-"}
            </span>
          )}
        </BaseColumn>
        <TextColumn
          id="worksapce"
          label={t("Workspace")}
          accessor="workspace.name"
          className="w-36"
        />
        <BaseColumn id="tags" label={t("Tags")} className="w-32">
          {(template) => (
            <div className="flex flex-wrap gap-1">
              {template.tags && template.tags.length > 0 ? (
                template.tags.slice(0, 2).map((tag: any) => (
                  <Tag key={tag.id} tag={tag} className="text-xs" />
                ))
              ) : (
                <span className="text-gray-400 text-xs">-</span>
              )}
              {template.tags && template.tags.length > 2 && (
                <span className="text-xs text-gray-500">+{template.tags.length - 2}</span>
              )}
            </div>
          )}
        </BaseColumn>
        <BaseColumn id="functionalType" label={t("Type")} className="w-28">
          {(template) => (
            <span className="text-gray-600 text-sm">
              {template.functionalType ? formatPipelineFunctionalType(template.functionalType) : <span className="text-gray-400">-</span>}
            </span>
          )}
        </BaseColumn>
        <DateColumn
          accessor={"currentVersion.createdAt"}
          label={t("Updated")}
          className="w-32"
        />
        <BaseColumn id="actions" className="text-right w-52">
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
                    {t("Create")}
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
