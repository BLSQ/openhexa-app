import { Popover as HeadlessPopover, Portal } from "@headlessui/react";
import { Placement, PositioningStrategy } from "@popperjs/core";
import clsx from "clsx";
import { ReactElement, ReactNode, useState } from "react";
import { usePopper } from "react-popper";

type PopoverProps = {
  trigger: ReactElement;
  placement?: Placement;
  className?: string;
  as?: any;
  buttonClassName?: string;
  strategy?: PositioningStrategy;
  withPortal?: boolean;
  children: ReactNode | ReactElement | ReactElement[];
};

const POPPER_MODIFIERS = [{ name: "offset", options: { offset: [0, 8] } }];

const Popover = (props: PopoverProps) => {
  const {
    trigger,
    placement = "bottom-end",
    withPortal = false,
    as,
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

  const panel = (
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
  );

  return (
    <HeadlessPopover className="relative">
      <HeadlessPopover.Button
        as={as}
        className={clsx("flex items-center outline-none", buttonClassName)}
        ref={setReferenceElement}
      >
        {trigger}
      </HeadlessPopover.Button>
      {withPortal ? <Portal>{panel}</Portal> : panel}
    </HeadlessPopover>
  );
};

export default Popover;
