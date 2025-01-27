import { useTranslation } from "next-i18next";
import React, { ReactElement } from "react";
import Block from "../Block";
import Link from "../Link";

type StatsProps = {
  count: string | number;
  url?: React.ComponentProps<typeof Link>["href"];
  label: string;
  icon?: ReactElement;
};

const Stats = (props: StatsProps) => {
  const { count, label, url, icon } = props;
  const { t } = useTranslation();
  return (
    <Block>
      <div className="flex gap-4 px-4 py-5">
        {icon && (
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-gray-100 p-2 text-gray-700">
            {icon}
          </div>
        )}
        <dl>
          <dt className="truncate text-sm font-medium text-gray-500">
            {label}
          </dt>
          <dd className="text-3xl font-semibold text-gray-700">
            {url ? (
              <Link customStyle="hover:text-gray-600" href={url}>
                {count}
              </Link>
            ) : (
              count
            )}
          </dd>
        </dl>
      </div>
      {url && (
        <div className="border-t border-gray-100 bg-gray-50 px-4 py-2 pb-3">
          <Link className="text-sm" href={url}>
            {t("View all")}
          </Link>
        </div>
      )}
    </Block>
  );
};

export default Stats;
