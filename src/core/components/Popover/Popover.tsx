import {
  Popover as HeadlessPopover,
  PopoverButton as HeadlessPopoverButton,
  PopoverPanel as HeadlessPopoverPanel,
  Portal,
} from "@headlessui/react";
import { Placement, PositioningStrategy } from "@popperjs/core";
import clsx from "clsx";
import React, { useState } from "react";
import { usePopper } from "react-popper";

type PopoverProps = {
  trigger: React.ComponentProps<typeof HeadlessPopoverButton>["children"];
  placement?: Placement;
  className?: string;
  as?: any;
  buttonClassName?: string;
  strategy?: PositioningStrategy;
  withPortal?: boolean;
  children: React.ComponentProps<typeof HeadlessPopoverPanel>["children"];
};

const POPPER_MODIFIERS = [{ name: "offset", options: { offset: [0, 6] } }];

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
  const [popperElement, setPopperElement] = useState<HTMLElement | null>(null);
  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    placement,
    modifiers: POPPER_MODIFIERS,
    strategy,
  });

  const panel = (
    <HeadlessPopoverPanel
      ref={setPopperElement}
      style={styles.popper}
      className={clsx(
        "z-10 overflow-hidden rounded-md bg-white p-4 shadow-md ring-1 ring-black/5",
        className,
      )}
      {...attributes.popper}
    >
      {children}
    </HeadlessPopoverPanel>
  );

  return (
    <HeadlessPopover className="relative">
      <HeadlessPopoverButton
        as={as}
        className={clsx("flex items-center outline-hidden", buttonClassName)}
        ref={setReferenceElement}
      >
        {trigger}
      </HeadlessPopoverButton>
      {withPortal ? <Portal>{panel}</Portal> : panel}
    </HeadlessPopover>
  );
};

export default Popover;
