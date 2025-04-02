import {
  Listbox as UIListbox,
  ListboxButton as UIListboxButton,
  ListboxOption as UIListboxOption,
  ListboxOptions as UIListboxOptions,
  Portal,
} from "@headlessui/react";
import { ChevronUpDownIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import { sameWidthModifier } from "core/helpers/popper";
import { usePopper } from "react-popper";
import useIntersectionObserver from "core/hooks/useIntersectionObserver";

type ListboxProps = {
  value: any;
  options: any[];
  getOptionLabel(value?: any): string;
  by: string;
  placeholder?: string;
  onChange(value: any): void;
  onScrollBottom?(): void;
  className?: string;
};

const MODIFIERS = [
  { name: "offset", options: { offset: [0, 4] } },
  sameWidthModifier,
];

const Listbox = (props: ListboxProps) => {
  const { t } = useTranslation();
  const {
    getOptionLabel,
    value,
    options,
    onScrollBottom,
    onChange,
    className,
    by,
    placeholder = t("Select..."),
  } = props;
  const [referenceElement, setReferenceElement] =
    useState<HTMLDivElement | null>(null);
  const [popperElement, setPopperElement] = useState<HTMLElement | null>(null);

  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    strategy: "fixed",
    placement: "bottom-start",
    modifiers: MODIFIERS,
  });

  return (
    <UIListbox value={value} onChange={onChange} by={by}>
      {({ open }) => (
        <div ref={setReferenceElement}>
          <UIListboxButton
            className={clsx(
              "form-input relative w-full  cursor-default rounded-md bg-white px-3 py-2 pr-10 text-left disabled:cursor-not-allowed disabled:opacity-50 sm:text-sm",
              "focus:ring-blue-500",
              "text-gray-500",
              open
                ? "border-blue-500 ring-1 ring-blue-500"
                : "border-gray-300 hover:border-gray-400",
              !value && "text-gray-600/70",
              className,
            )}
          >
            <span className="block truncate">
              {value ? getOptionLabel(value) : placeholder}
            </span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2 text-gray-400 hover:text-gray-600">
              <ChevronUpDownIcon className="h-5 w-5" aria-hidden="true" />
            </span>
          </UIListboxButton>
          {open && (
            <Portal>
              <UIListboxOptions
                ref={setPopperElement}
                className={
                  "z-10 flex max-h-72 w-full flex-col rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black/5 focus:outline-hidden sm:text-sm"
                }
                style={styles.popper}
                {...attributes.popper}
              >
                <div className="flex-1 overflow-auto">
                  {options.map((option) => (
                    <UIListboxOption
                      key={option[by]}
                      value={option}
                      className={({ focus }) =>
                        clsx(
                          "relative cursor-default select-none px-2 py-2",
                          focus ? "bg-blue-500 text-white" : "text-gray-900",
                        )
                      }
                    >
                      {({ focus, selected }) => (
                        <span
                          className={clsx(
                            "flex-1 truncate",
                            selected && "font-semibold",
                          )}
                        >
                          {getOptionLabel(option)}
                        </span>
                      )}
                    </UIListboxOption>
                  ))}
                  {onScrollBottom && (
                    <IntersectionObserverWrapper
                      onScrollBottom={onScrollBottom}
                    />
                  )}
                </div>
              </UIListboxOptions>
            </Portal>
          )}
        </div>
      )}
    </UIListbox>
  );
};

const IntersectionObserverWrapper = ({
  onScrollBottom,
}: {
  onScrollBottom: () => void;
}) => {
  const [lastElement, setLastElement] = useState<Element | null>(null);
  const list = useIntersectionObserver(lastElement, {});

  useEffect(() => {
    if (lastElement && list?.isIntersecting) {
      onScrollBottom();
    }
  }, [onScrollBottom, list, lastElement]);

  return <div ref={setLastElement}></div>;
};

export default Listbox;
