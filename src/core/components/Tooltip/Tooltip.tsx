import { Transition } from "@headlessui/react";
import ReactDOM from "react-dom";
import React, { LegacyRef, ReactElement, ReactNode } from "react";
import { Config, usePopperTooltip } from "react-popper-tooltip";

import styles from "./Tooltip.module.css";

type Props = {
  label: ReactNode;
  as?: string;
} & Config &
  (
    | { children: ReactElement }
    | { renderTrigger: (ref: LegacyRef<HTMLElement>) => ReactNode }
  );

const Tooltip = (props: Props) => {
  const { label, as = "button", ...delegated } = props;
  const {
    getArrowProps,
    getTooltipProps,
    setTooltipRef,
    setTriggerRef,
    visible,
  } = usePopperTooltip(delegated);

  return (
    <>
      {"children" in props
        ? React.createElement(
            as,
            { type: "button", ref: setTriggerRef },
            props.children
          )
        : props.renderTrigger(setTriggerRef)}
      {typeof window !== "undefined" &&
        ReactDOM.createPortal(
          <Transition
            show={visible}
            enter="transition-opacity duration-75"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity duration-150"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div
              ref={setTooltipRef}
              {...getTooltipProps({
                className: styles["tooltip"],
              })}
            >
              <div {...getArrowProps({ className: styles["arrow"] })} />
              {label}
            </div>
          </Transition>,
          document.body
        )}
    </>
  );
};

export default Tooltip;
