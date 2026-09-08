import { Fragment, ReactNode } from "react";

type DetailHeaderProps = {
  icon?: ReactNode;
  title: string;
  badges?: ReactNode;
  // Rendered on the second line, separated by vertical rules. Falsy entries are dropped.
  meta?: ReactNode[];
};

const DetailHeader = ({ icon, title, badges, meta }: DetailHeaderProps) => {
  const metaItems = (meta ?? []).filter(Boolean);

  return (
    <div className="flex items-center gap-3.5 border-b border-gray-100 px-5 py-4">
      {icon && (
        <div className="flex h-11 w-11 flex-none items-center justify-center overflow-hidden rounded-lg border border-gray-100 bg-white">
          {icon}
        </div>
      )}
      <div className="flex min-w-0 flex-col gap-0.5">
        <div className="flex items-center gap-2.5">
          <h2 className="truncate text-[19px] font-bold tracking-tight text-gray-900">
            {title}
          </h2>
          {badges}
        </div>
        {metaItems.length > 0 && (
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[13px]">
            {metaItems.map((item, index) => (
              <Fragment key={index}>
                {index > 0 && <span className="h-3.5 w-px bg-gray-200" />}
                {item}
              </Fragment>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DetailHeader;
