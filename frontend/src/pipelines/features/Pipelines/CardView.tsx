import React from "react";
import PipelineCard from "workspaces/features/PipelineCard";
import Pagination from "core/components/Pagination";

type CardViewProps = {
  items: any[];
  workspace: any;
  page: number;
  perPage: number;
  totalItems: number;
  setPage: (page: number) => void;
};

const CardView = ({
  items,
  workspace,
  page,
  perPage,
  setPage,
  totalItems,
}: CardViewProps) => {
  return (
    <>
      <div className="mt-5 mb-3 grid grid-cols-2 gap-4 xl:grid-cols-3 xl:gap-5">
        {items.map((pipeline, index) => (
          <PipelineCard workspace={workspace} key={index} pipeline={pipeline} />
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
  );
};

export default CardView;
