import React from "react";
import TemplateCard from "workspaces/features/TemplateCard";
import Pagination from "core/components/Pagination";
import { useTranslation } from "next-i18next";

type CardViewProps = {
  items: any[];
  workspace: any;
  page: number;
  perPage: number;
  totalItems: number;
  createPipeline: (pipelineTemplateVersionId: string) => () => void;
  setPage: (page: number) => void;
};

const CardView = ({
  items,
  workspace,
  page,
  perPage,
  totalItems,
  createPipeline,
  setPage,
}: CardViewProps) => {
  const { t } = useTranslation();

  return (
    <>
      {items.length === 0 ? (
        <div className="text-center text-gray-500 mt-20">
          <div>{t("No template to show")}</div>
        </div>
      ) : (
        <>
          <div className="mt-5 mb-3 grid grid-cols-2 gap-4 xl:grid-cols-3 xl:gap-5">
            {items.map((template, index) => (
              <TemplateCard
                workspace={workspace}
                key={index}
                template={template}
                onCreate={
                  template.currentVersion?.id
                    ? createPipeline(template.currentVersion?.id)
                    : undefined
                }
              />
            ))}
          </div>
          <Pagination
            onChange={(page) => setPage(page)}
            page={page}
            perPage={perPage}
            totalItems={totalItems}
            countItems={items.length}
          />
        </>
      )}
    </>
  );
};

export default CardView;
