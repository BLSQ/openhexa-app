import React from "react";
import Pagination from "core/components/Pagination";

type WorkspacesPaginationProps = {
  page: number;
  totalItems: number;
  perPage: number;
  onPageChange: (page: number) => void;
};

const WorkspacesPagination = ({
  page,
  totalItems,
  perPage,
  onPageChange,
}: WorkspacesPaginationProps) => {
  const totalPages = Math.ceil(totalItems / perPage);
  const countItems = Math.min(perPage, totalItems - (page - 1) * perPage);

  if (totalPages <= 1) {
    return null;
  }

  return (
    <div className="flex justify-center mt-6">
      <Pagination
        page={page}
        perPage={perPage}
        totalPages={totalPages}
        countItems={countItems}
        totalItems={totalItems}
        onChange={(newPage) => onPageChange(newPage)}
      />
    </div>
  );
};

export default WorkspacesPagination;