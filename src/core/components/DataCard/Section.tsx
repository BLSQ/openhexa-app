import { Disclosure, Transition } from "@headlessui/react";
import { ChevronDownIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

import { useTranslation } from "next-i18next";
import { ReactElement } from "react";
import Block from "../Block";
import Spinner from "../Spinner";

type SectionProps = {
  className?: string;
  children?: null | (({ open }: { open: boolean }) => ReactElement | null);
  defaultOpen?: boolean;
  loading?: boolean;
  title?: string | (({ open }: { open: boolean }) => ReactElement);
};

function Section(props: SectionProps) {
  const { t } = useTranslation();
  const { title, className, children, defaultOpen = true, loading } = props;

  return (
    <Block.Content className={className}>
      <Disclosure defaultOpen={defaultOpen}>
        {({ open }) => (
          <>
            {title && (
              <Disclosure.Button
                as="div"
                className="-my-7 flex items-center py-7"
              >
                {typeof title === "function" ? (
                  title({ open })
                ) : (
                  <>
                    <h4 className="font-medium">{title}</h4>
                    <div className="flex flex-1 flex-shrink items-center justify-end">
                      {loading ? (
                        <Spinner size="sm" />
                      ) : (
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
                )}
              </Disclosure.Button>
            )}
            {children && (
              <Transition
                show={open}
                enter="transition duration-75 ease-out"
                enterFrom="transform opacity-0"
                enterTo="transform opacity-100"
                leave="transition duration-50 ease-out"
                leaveFrom="transform opacity-100"
                leaveTo="transform opacity-0"
              >
                <Disclosure.Panel static className={clsx(title && "mt-6")}>
                  {children({ open })}
                </Disclosure.Panel>
              </Transition>
            )}
          </>
        )}
      </Disclosure>
    </Block.Content>
  );
}

export default Section;
