import {
  Tab as HeadlessTab,
  TabGroup as HeadlessTabGroup,
  TabList as HeadlessTabList,
  TabPanel as HeadlessTabPanel,
  TabPanels as HeadlessTabPanels,
} from "@headlessui/react";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import React, {
  Fragment,
  isValidElement,
  ReactElement,
  ReactNode,
  useMemo,
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

  const validChildren: React.ReactNode[] = useMemo(
    () =>
      React.Children.toArray(children).filter((child: React.ReactNode) =>
        isValidElement(child),
      ),
    [children],
  );

  return (
    // HeadlessTabGroup is a wrapper for the tabs and panels. To not break Sentry, we need to add the as="div" prop.
    <HeadlessTabGroup
      as={"div"}
      defaultIndex={defaultIndex}
      onChange={onChange}
    >
      <HeadlessTabList
        className={clsx(
          "border-b border-gray-200 text-sm font-medium ",
          className,
        )}
      >
        <nav className="-mb-px flex space-x-8" aria-label={t("Tabs")}>
          {React.Children.map(
            validChildren,
            (child, idx) =>
              isValidElement(child) && (
                <HeadlessTab as={Fragment} key={idx}>
                  {({ selected }) => (
                    <a
                      className={clsx(
                        "cursor-pointer whitespace-nowrap border-b-2 px-1.5 py-2.5 hover:text-gray-900 tracking-wide",
                        selected
                          ? "border-pink-500 "
                          : "border-transparent text-gray-500 hover:border-gray-400",
                      )}
                    >
                      {child.props.label}
                    </a>
                  )}
                </HeadlessTab>
              ),
          )}
        </nav>
      </HeadlessTabList>
      <HeadlessTabPanels>
        {React.Children.map(validChildren, (child) => (
          <HeadlessTabPanel>{child}</HeadlessTabPanel>
        ))}
      </HeadlessTabPanels>
    </HeadlessTabGroup>
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
