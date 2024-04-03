import { ReactNode, useEffect, ReactElement } from "react";

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

export default OptionsWrapper;
