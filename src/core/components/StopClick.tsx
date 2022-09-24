import React, { FunctionComponent, ReactElement, useCallback } from "react";

type StopClickProps = {
  children?: ReactElement | boolean;
  className?: string;
  as?: string | FunctionComponent;
};

const StopClick = (props: StopClickProps) => {
  const { className, as = "div", children } = props;

  const handler = useCallback(
    (event: { stopPropagation: Function; preventDefault: Function }) => {
      console.log("called");
      event.preventDefault();
      event.stopPropagation();
    },
    []
  );
  return React.createElement<any>(
    as,
    { className, onClick: handler, onMouseDown: handler, onMouseUp: handler },
    children
  );
};

export default StopClick;
