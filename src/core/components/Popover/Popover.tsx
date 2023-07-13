import { Popover as HeadlessPopover, Transition } from "@headlessui/react";
import { Placement, PositioningStrategy } from "@popperjs/core";
import clsx from "clsx";
import { Fragment, ReactElement, ReactNode, useState } from "react";
import { usePopper } from "react-popper";

type PopoverProps = {
  trigger: ReactElement;
  placement?: Placement;
  className?: string;
  buttonClassName?: string;
  strategy?: PositioningStrategy;
  children: ReactNode | ReactElement | ReactElement[];
};

const POPPER_MODIFIERS = [{ name: "offset", options: { offset: [0, 8] } }];

const Popover = (props: PopoverProps) => {
  const {
    trigger,
    placement = "bottom-end",
    strategy,
    className,
    buttonClassName,
    children,
  } = props;
  const [referenceElement, setReferenceElement] =
    useState<HTMLButtonElement | null>(null);
  const [popperElement, setPopperElement] = useState<HTMLDivElement | null>(
    null
  );
  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    placement,
    modifiers: POPPER_MODIFIERS,
    strategy,
  });

  return (
    <HeadlessPopover className="relative">
      <HeadlessPopover.Button
        className={clsx("flex items-center", buttonClassName)}
        ref={setReferenceElement}
      >
        {trigger}
      </HeadlessPopover.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-200"
        enterFrom="opacity-0 translate-y-1"
        enterTo="opacity-100 translate-y-0"
        leave="transition ease-in duration-150"
        leaveFrom="opacity-100 translate-y-0"
        leaveTo="opacity-0 translate-y-1"
      >
        <HeadlessPopover.Panel
          ref={setPopperElement}
          style={styles.popper}
          className={clsx(
            "overflow-hidden rounded-lg bg-white p-4 shadow-lg ring-1 ring-black ring-opacity-5",
            className
          )}
          {...attributes.popper}
        >
          {children}
        </HeadlessPopover.Panel>
      </Transition>
    </HeadlessPopover>
  );
};

export default Popover;
