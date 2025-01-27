import {
  Combobox as UICombobox,
  ComboboxButton as UIComboboxButton,
  ComboboxInput as UIComboboxInput,
  ComboboxOptions as UIComboboxOptions,
  Portal,
} from "@headlessui/react";
import { ChevronUpDownIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { Modifier } from "@popperjs/core";
import clsx from "clsx";
import Badge from "core/components/Badge";
import Spinner from "core/components/Spinner";
import { sameWidthModifier } from "core/helpers/popper";
import {
  ChangeEvent,
  Fragment,
  ReactNode,
  useCallback,
  useMemo,
  useRef,
  useState,
} from "react";
import { usePopper } from "react-popper";
import CheckOption from "./CheckOption";
import OptionsWrapper from "./OptionsWrapper";

type MultiComboboxProps<T> = {
  onInputChange: (event: ChangeEvent<HTMLInputElement>) => void;
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
  by?: (keyof T & string) | ((a: T, z: T) => boolean);
  onOpen?: () => void;
  displayValue(value: T): ReactNode;
  onClose?: () => void;
  placeholder?: string;
  withPortal?: boolean;
  className?: string;
  value: T[];
  onChange(value: T[]): void;
};

const Classes = {
  Options:
    "max-h-60 z-10 w-full rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black/5 focus:outline-hidden sm:text-sm flex flex-col",
  OptionsList: "overflow-auto flex-1",
};

function MultiCombobox<T extends { [key: string]: any }>(
  props: MultiComboboxProps<T>,
) {
  const {
    loading = false,
    required = false,
    withPortal = false,
    children,
    footer,
    onOpen,
    onClose,
    onInputChange,
    className,
    value,
    displayValue,
    placeholder,
    onChange,
    disabled,
    name,
    by,
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

  const onClear = useCallback(() => onChange([]), [onChange]);
  const close = useCallback(() => btnRef.current?.click(), [btnRef]);
  const onRemoveItem = useCallback(
    (item: T) => {
      value && onChange(value.filter((x) => x !== item));
    },
    [onChange, value],
  );

  const optionsElement = (
    <UIComboboxOptions
      className={Classes.Options}
      ref={setPopperElement}
      style={styles.popper}
      data-testid="combobox-options"
      {...attributes.popper}
    >
      <div className={Classes.OptionsList}>
        <OptionsWrapper onOpen={onOpen} onClose={onClose}>
          {children}
        </OptionsWrapper>
      </div>
      {footer && footer({ close, clear: onClear })}
    </UIComboboxOptions>
  );

  return (
    <UICombobox<T[]>
      onChange={onChange}
      value={value}
      disabled={disabled}
      multiple={true as any}
      name={name}
      by={by as any}
    >
      {({ open }) => (
        <div className={clsx("relative", className)} ref={setReferenceElement}>
          <div
            className={clsx(
              "form-input flex w-full items-center rounded-md border-gray-300 shadow-xs disabled:border-gray-300",
              "focus-within:outline-hidden focus:ring-transparent focus-visible:border-blue-500 disabled:cursor-not-allowed ",
              "sm:text-sm",
              open ? "border-blue-500" : "hover:border-gray-400",
            )}
          >
            <div className="mr-1 flex flex-1 flex-wrap items-center gap-2 truncate">
              {value?.map((val, i) => (
                <Badge
                  className="bg-gray-100 py-0 hover:bg-gray-50 ring-gray-500/20"
                  key={i}
                >
                  {displayValue(val)}
                  {!disabled && !required && (
                    <XMarkIcon
                      className="ml-1 h-3 w-3 cursor-pointer"
                      onClick={() => onRemoveItem(val)}
                    />
                  )}
                </Badge>
              ))}
              <UIComboboxInput as={Fragment} onChange={onInputChange}>
                <input
                  data-testid="combobox-input"
                  className="flex-1 placeholder-gray-600/70 outline-hidden"
                  autoComplete="off"
                  placeholder={placeholder}
                />
              </UIComboboxInput>
            </div>
            <UIComboboxButton ref={btnRef} data-testid="combobox-button">
              <div className="ml-1 flex items-center gap-0.5 rounded-r-md text-gray-400 focus:outline-hidden">
                {(Array.isArray(value) ? value?.length > 0 : value) && (
                  <XMarkIcon
                    onClick={() => onChange([])}
                    className="h-4 w-4 cursor-pointer hover:text-gray-500"
                    aria-hidden="true"
                  />
                )}
                {loading ? (
                  <Spinner aria-hidden="true" size="sm" />
                ) : (
                  <ChevronUpDownIcon
                    className="h-5 w-5 hover:text-gray-500"
                    aria-hidden="true"
                  />
                )}
              </div>
            </UIComboboxButton>
          </div>

          {withPortal ? <Portal>{optionsElement}</Portal> : optionsElement}
        </div>
      )}
    </UICombobox>
  );
}

MultiCombobox.CheckOption = CheckOption;

export default MultiCombobox;
