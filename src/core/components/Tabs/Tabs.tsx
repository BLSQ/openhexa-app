import { Tab as HeadlessTab } from "@headlessui/react";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import React, {
  Fragment,
  isValidElement,
  ReactElement,
  ReactNode,
} from "react";

export type TabsProps = {
  children: ReactNode;
  defaultIndex?: number;
  onChange?: (index: number) => void;
  className?: string;
};

const Tabs = (props: TabsProps) => {
  const { children, defaultIndex = 0, onChange, className } = props;
  const { t } = useTranslation();
  return (
    <HeadlessTab.Group defaultIndex={defaultIndex} onChange={onChange}>
      <HeadlessTab.List
        className={clsx(
          "border-b border-gray-200 text-sm font-medium ",
          className
        )}
      >
        <nav className="-mb-px flex space-x-8" aria-label={t("Tabs")}>
          {React.Children.map(children, (child, idx) =>
            isValidElement(child) ? (
              <HeadlessTab as={Fragment} key={idx}>
                {({ selected }) => (
                  <a
                    className={clsx(
                      "cursor-pointer whitespace-nowrap border-b-2 px-1.5 py-2.5 tracking-wide",
                      selected
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                    )}
                  >
                    {child.props.label}
                  </a>
                )}
              </HeadlessTab>
            ) : null
          )}
        </nav>
      </HeadlessTab.List>
      <HeadlessTab.Panels>
        {React.Children.map(children, (child) => (
          <HeadlessTab.Panel>{child}</HeadlessTab.Panel>
        ))}
      </HeadlessTab.Panels>
    </HeadlessTab.Group>
  );
};

type TabProps = {
  label: string;
  className?: string;
  children: ReactElement | ReactElement[];
};

function Tab(props: TabProps) {
  // props.label is used to set the label of the tab in the tabs bar
  const { children, className } = props;

  return <div className={className}>{children}</div>;
}

Tabs.Tab = Tab;

export default Tabs;
