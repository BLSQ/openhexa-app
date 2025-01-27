import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Transition,
} from "@headlessui/react";
import { ChevronDownIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

import { useTranslation } from "next-i18next";
import { ReactElement, ReactNode } from "react";
import BlockContent from "./BlockContent";
import Spinner from "../Spinner";

type BlockSectionProps = {
  className?: string;
  collapsible?: boolean;
  children?:
    | null
    | (({ open }: { open: boolean }) => ReactElement | null)
    | ReactNode;
  defaultOpen?: boolean;
  loading?: boolean;
  title?: string | (({ open }: { open: boolean }) => ReactElement | null);
};

function BlockSection(props: BlockSectionProps) {
  const { t } = useTranslation();
  const {
    title,
    collapsible = true,
    className,
    children,
    defaultOpen = true,
    loading,
  } = props;

  const renderHeader = (open: boolean) => {
    const header =
      typeof title === "function" ? (
        title({ open })
      ) : (
        <>
          <h4 className="font-medium">{title}</h4>
          <div className="flex flex-1 shrink items-center justify-end">
            {loading && <Spinner size="sm" />}
            {!loading && collapsible && (
              <button title={open ? t("Hide") : t("Show")}>
                {open ? (
                  <ChevronDownIcon className="h-5 w-5" />
                ) : (
                  <ChevronRightIcon className="h-5 w-5" />
                )}
              </button>
            )}
          </div>
        </>
      );
    return collapsible ? (
      <DisclosureButton as="div" className="-my-7 flex items-center py-7">
        {header}
      </DisclosureButton>
    ) : (
      <div className="-my-7 flex items-center py-7">{header}</div>
    );
  };

  return (
    <BlockContent className={className}>
      <Disclosure defaultOpen={defaultOpen || !collapsible}>
        {({ open }) => (
          <>
            {title && renderHeader(open)}
            {children && (
              <Transition
                show={open}
                enter="transition duration-75 ease-out"
                enterFrom="transform opacity-0"
                enterTo="transform opacity-100"
                leave="transition duration-50 ease-out"
                leaveFrom="transform opacity-100"
                leaveTo="transform opacity-0"
                as="div"
              >
                <DisclosurePanel static className={clsx(title && "mt-6")}>
                  {typeof children === "function"
                    ? children({ open })
                    : children}
                </DisclosurePanel>
              </Transition>
            )}
          </>
        )}
      </Disclosure>
    </BlockContent>
  );
}

export default BlockSection;
