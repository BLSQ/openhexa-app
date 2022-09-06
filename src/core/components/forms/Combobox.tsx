import { Combobox as UICombobox, Portal } from "@headlessui/react";
import { CheckIcon, SelectorIcon, XIcon } from "@heroicons/react/outline";
import { Modifier } from "@popperjs/core";
import clsx from "clsx";
import Spinner from "core/components/Spinner";
import { sameWidthModifier } from "core/helpers/popper";
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
import { usePopper } from "react-popper";

type ComboboxProps<T = {}> = {
  value: T | T[] | null;
  onChange: (value: T | T[] | null) => void;
  onInputChange: (event: ChangeEvent<HTMLInputElement>) => void;
  multiple?: boolean;
  required?: boolean;
  name?: string;
  disabled?: boolean;
  children: ReactNode;
  footer?: ({
    close,
    clear,
  }: {
    close: () => void;
    clear: () => void;
  }) => ReactNode;
  loading?: boolean;
  by?: string;
  renderIcon?: ({
    value,
  }: {
    value: T | T[] | null;
  }) => ReactElement | undefined | null;
  onOpen?: () => void;
  onClose?: () => void;
  placeholder?: string;
  displayValue: (value: T | T[] | null) => string;
  withPortal?: boolean;
  className?: string;
};

const OptionsWrapper = (props: {
  onOpen?: () => void;
  onClose?: () => void;
  children: ReactElement | ReactNode | undefined;
}) => {
  const { onOpen, onClose, children } = props;

  useEffect(() => {
    onOpen && onOpen();
    return onClose;
  }, [onOpen, onClose]);

  return <>{children}</>;
};

const Classes = {
  Options:
    "max-h-60 z-10 w-full rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm flex flex-col",
  OptionsList: "overflow-auto flex-1",
};

function Combobox<T>(props: ComboboxProps<T>) {
  const {
    loading = false,
    required = false,
    withPortal = false,
    children,
    footer,
    onOpen,
    onClose,
    onInputChange,
    displayValue,
    className,
    renderIcon,
    multiple,
    value,
    placeholder,
    onChange,
    ...delegated
  } = props;

  const btnRef = useRef<HTMLButtonElement>(null);
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

  const onClear = useCallback(() => {
    onChange(null);
  }, [onChange]);
  const close = useCallback(() => {
    btnRef.current?.click();
  }, [btnRef]);

  const optionsElement = (
    <UICombobox.Options
      className={Classes.Options}
      ref={setPopperElement}
      style={styles.popper}
      {...attributes.popper}
    >
      <div className={Classes.OptionsList}>
        <OptionsWrapper onOpen={onOpen} onClose={onClose}>
          {children}
        </OptionsWrapper>
      </div>
      {footer && footer({ close, clear: onClear })}
    </UICombobox.Options>
  );

  return (
    <UICombobox
      {...delegated}
      onChange={onChange}
      value={value}
      as="div"
      nullable={!required}
      multiple={multiple}
    >
      {({ open }) => (
        <div className="relative" ref={setReferenceElement}>
          <div
            className={clsx(
              "form-input flex w-full items-center rounded-md border-gray-300 shadow-sm disabled:border-gray-300",
              "focus-within:outline-none focus:ring-transparent focus-visible:border-blue-500 disabled:cursor-not-allowed ",
              "sm:text-sm",
              open ? "border-blue-500" : "hover:border-gray-400"
            )}
          >
            <div className="mr-1 flex flex-1 items-center truncate">
              <UICombobox.Input
                as={Fragment}
                onChange={onInputChange}
                displayValue={displayValue}
              >
                <input
                  className="flex-1 placeholder-gray-600 placeholder-opacity-70 outline-none"
                  autoComplete="off"
                  placeholder={placeholder}
                />
              </UICombobox.Input>
            </div>
            {renderIcon && renderIcon({ value })}
            <UICombobox.Button ref={btnRef}>
              <div className="ml-1 flex items-center gap-0.5 rounded-r-md text-gray-400 focus:outline-none">
                {(Array.isArray(value) ? value?.length > 0 : value) && (
                  <XIcon
                    onClick={() => onChange(multiple ? [] : null)}
                    className="h-4 w-4 cursor-pointer hover:text-gray-500"
                    aria-hidden="true"
                  />
                )}
                {loading ? (
                  <Spinner aria-hidden="true" size="sm" />
                ) : (
                  <SelectorIcon
                    className="h-5 w-5 hover:text-gray-500"
                    aria-hidden="true"
                  />
                )}
              </div>
            </UICombobox.Button>
          </div>

          {withPortal ? <Portal>{optionsElement}</Portal> : optionsElement}
        </div>
      )}
    </UICombobox>
  );
}

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
          active ? "bg-blue-500 text-white" : "text-gray-900",
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
                (selected || forceSelected) && !active && "text-blue-500"
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
