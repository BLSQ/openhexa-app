import Link from "core/components/Link";
import clsx from "clsx";

type LinkTabProps = {
  selected?: string;
  tabs: { label: string; href: string; id: string }[];
  className?: string;
};

const LinkTabs = ({ tabs, selected, className }: LinkTabProps) => {
  return (
    <div
      className={clsx("flex space-x-8 -mb-px text-sm font-medium", className)}
    >
      {tabs.map((tab) => (
        <Link
          key={tab.id}
          href={tab.href}
          className={clsx(
            "whitespace-nowrap cursor-pointer border-b-2 px-1.5 pt-2.5 pb-2 tracking-wide first:pl-0  first:ml-1.5 hover:text-gray-900",
            tab.id === selected
              ? "border-pink-500 text-gray-900 font-medium"
              : "border-transparent text-gray-500 hover:border-gray-400",
          )}
        >
          {tab.label}
        </Link>
      ))}
    </div>
  );
};

export default LinkTabs;
