import { Combobox as UICombobox } from "@headlessui/react";
import { CheckIcon, SelectorIcon } from "@heroicons/react/outline";
import clsx from "clsx";
import Spinner from "core/components/Spinner";
import { usePopper } from "react-popper";
import {
  ChangeEvent,
  Fragment,
  ReactElement,
  ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import Input from "./Input";
import { sameWidthModifier } from "core/helpers/popper";
import { createPortal } from "react-dom";
import { Modifier } from "@popperjs/core";

type ComboboxProps = {
  value: any;
  onChange: (value: any) => void;
  onInputChange: (event: ChangeEvent<HTMLInputElement>) => void;
  multiple?: boolean;
  required?: boolean;
  name?: string;
  disabled?: boolean;
  children: ReactNode;
  loading?: boolean;
  renderIcon?: ({ value }: { value: any }) => ReactElement | undefined | null;
  onOpen?: () => void;
  onClose?: () => void;
  placeholder?: string;
  displayValue: (value: any) => string;
  withPortal?: boolean;
};

const OptionsWrapper = (props: {
  onOpen?: () => void;
  onClose?: () => void;
  open: boolean;
  children: ReactElement;
}) => {
  const { onOpen, onClose, open, children } = props;
  const [isMounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    // Don't call event handlers if we just mounted the component
    if (!isMounted) return;

    if (open) {
      onOpen && onOpen();
    } else {
      onClose && onClose();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, onOpen, onClose]);

  return children;
};

const Classes = {
  Button:
    "absolute inset-y-0 right-0 flex items-center rounded-r-md px-2 focus:outline-none text-gray-400 hover:text-gray-500",
  Options:
    "max-h-60 z-10 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm",
};

const Combobox = (props: ComboboxProps) => {
  const {
    loading = false,
    required = false,
    withPortal = false,
    children,
    onOpen,
    onClose,
    onInputChange,
    displayValue,
    renderIcon,
    value,
    placeholder,
    ...delegated
  } = props;

  const btnRef = useRef<HTMLButtonElement>(null);
  const openRef = useRef<boolean>(false);
  const [referenceElement, setReferenceElement] =
    useState<HTMLDivElement | null>(null);
  const [popperElement, setPopperElement] = useState<HTMLElement | null>(null);

  const modifiers = useMemo(() => {
    return [
      { name: "offset", options: { offset: [0, 4] } },
      withPortal && sameWidthModifier,
    ].filter(Boolean) as Modifier<any, any>[];
  }, [withPortal]);

  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    strategy: withPortal ? "fixed" : "absolute",
    placement: "bottom-start",
    modifiers,
  });

  const handleFocus = useCallback(() => {
    // Simulate a click on the button to open the menu ...
    // ... when the user focuses the input (and do nothing ...
    // ... when the user already clicked on the button)
    if (!openRef.current) btnRef.current?.click();
  }, [btnRef]);

  const icon = useMemo(() => {
    if (loading) {
      return <Spinner size="xs" />;
    } else if (renderIcon) {
      return renderIcon({ value });
    }
  }, [loading, renderIcon, value]);

  const optionsElement = (
    <UICombobox.Options
      className={Classes.Options}
      ref={setPopperElement}
      style={styles.popper}
      {...attributes.popper}
    >
      {({ open }) => {
        openRef.current = open; // Store the last 'open' value to avoid to "double trigger" the open event
        return (
          <OptionsWrapper open={open} onOpen={onOpen} onClose={onClose}>
            <>{children}</>
          </OptionsWrapper>
        );
      }}
    </UICombobox.Options>
  );
  return (
    <UICombobox {...delegated} value={value} as="div" nullable={!required}>
      <div className="relative" ref={setReferenceElement}>
        <UICombobox.Input
          as={Fragment}
          onChange={onInputChange}
          displayValue={displayValue}
        >
          <Input
            placeholder={placeholder}
            onFocus={handleFocus}
            trailingIcon={
              <UICombobox.Button className={Classes.Button} ref={btnRef}>
                {icon ?? (
                  <SelectorIcon className="h-5 w-5 " aria-hidden="true" />
                )}
              </UICombobox.Button>
            }
          />
        </UICombobox.Input>
        {typeof window !== "undefined" && withPortal
          ? createPortal(optionsElement, document.body)
          : optionsElement}
      </div>
    </UICombobox>
  );
};

type CheckOptionsProps = {
  value: any;
  className?: string;
  disabled?: boolean;
  forceSelected?: boolean;
  children?:
    | ReactNode
    | (({
        active,
        selected,
      }: {
        active: boolean;
        selected: boolean;
      }) => ReactNode);
};

Combobox.CheckOption = function CheckOption(props: CheckOptionsProps) {
  const {
    value,
    className,
    children,
    disabled = false,
    forceSelected = false,
  } = props;

  return (
    <UICombobox.Option
      value={value}
      disabled={disabled}
      className={({ active }) =>
        clsx(
          "relative cursor-default select-none px-2 py-2",
          active ? "bg-lochmara text-white" : "text-gray-900",
          className
        )
      }
    >
      {({ active, selected }) => (
        <div className="group flex w-full items-center">
          <span
            className={clsx(
              "flex items-center pr-4",
              !selected && !forceSelected && "invisible",
              active ? "text-white" : "text-gray-900"
            )}
          >
            <CheckIcon
              className={clsx(
                "h-5 w-5",
                (selected || forceSelected) && !active && "text-lochmara"
              )}
              aria-hidden="true"
            />
          </span>
          <span
            className={clsx(
              "flex-1 truncate",
              (selected || forceSelected) && "font-semibold"
            )}
          >
            {typeof children === "function"
              ? children({ active, selected: selected || forceSelected })
              : children}
          </span>
        </div>
      )}
    </UICombobox.Option>
  );
};

export default Combobox;
