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
import Spinner from "core/components/Spinner";
import { sameWidthModifier } from "core/helpers/popper";
import {
  ChangeEvent,
  Fragment,
  ReactElement,
  ReactNode,
  useCallback,
  useMemo,
  useRef,
  useState,
} from "react";
import { usePopper } from "react-popper";
import CheckOption from "./CheckOption";
import OptionsWrapper from "./OptionsWrapper";

export type ComboboxProps<T> = {
  renderIcon?(value?: T): ReactElement;
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
  displayValue(value: T): string;
  onClose?: () => void;
  placeholder?: string;
  withPortal?: boolean;
  className?: string;
  value?: T | null;
  onChange(value?: T | null): void;
};

const Classes = {
  Options:
    "max-h-60 z-10 w-full rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black/5 focus:outline-hidden sm:text-sm flex flex-col",
  OptionsList: "overflow-auto flex-1",
};

function Combobox<T extends { [key: string]: any }>(props: ComboboxProps<T>) {
  const {
    loading = false,
    withPortal = false,
    children,
    footer,
    onOpen,
    onClose,
    onInputChange,
    displayValue,
    renderIcon,
    value,
    placeholder,
    onChange,
    by,
    required,
    disabled,
    className,
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

  const onClear = useCallback(() => onChange(), [onChange]);
  const close = useCallback(() => btnRef.current?.click(), [btnRef]);

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
      {footer && footer({ close, clear: () => onClear })}
    </UIComboboxOptions>
  );

  return (
    <UICombobox
      onChange={onChange}
      value={value}
      multiple={false}
      disabled={disabled}
      by={by as any /* Otherwise typescript is not happy */}
      {...delegated}
    >
      {({ open }) => (
        <div className="relative" ref={setReferenceElement}>
          <div
            className={clsx(
              "form-input flex w-full items-center rounded-md border-gray-300 shadow-xs disabled:border-gray-300",
              "focus-within:outline-hidden focus:ring-transparent focus-visible:border-blue-500 disabled:cursor-not-allowed ",
              "sm:text-sm",
              open ? "border-blue-500" : "hover:border-gray-400",
              className,
            )}
          >
            <div className="mr-1 flex flex-1 items-center truncate">
              <UIComboboxInput
                as={Fragment}
                onChange={onInputChange}
                displayValue={displayValue}
              >
                <input
                  data-testid="combobox-input"
                  className="flex-1 placeholder-gray-600/70 outline-hidden"
                  autoComplete="off"
                  placeholder={placeholder}
                />
              </UIComboboxInput>
            </div>
            {value && renderIcon && renderIcon(value)}
            <UIComboboxButton ref={btnRef} data-testid="combobox-button">
              <div className="ml-1 flex items-center gap-0.5 rounded-r-md text-gray-400 focus:outline-hidden">
                {value && !required && !disabled && (
                  <XMarkIcon
                    onClick={() => onChange()}
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

Combobox.CheckOption = CheckOption;

export default Combobox;
