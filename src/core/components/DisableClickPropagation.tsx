import React, { FunctionComponent, ReactElement, useCallback } from "react";

type DisableClickPropagationProps = {
  children?: ReactElement | boolean;
  className?: string;
  as?: string | FunctionComponent;
};

const DisableClickPropagation = (props: DisableClickPropagationProps) => {
  const { className, as = "div", children } = props;

  const handler = useCallback(
    (event: { stopPropagation: Function; preventDefault: Function }) => {
      event.preventDefault();
      event.stopPropagation();
    },
    [],
  );
  return React.createElement<any>(
    as,
    { className, onClick: handler, onMouseDown: handler, onMouseUp: handler },
    children,
  );
};

export default DisableClickPropagation;
