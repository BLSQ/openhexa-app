import { ReactNode, useEffect } from "react";
import { ReactElement } from "react-markdown/lib/react-markdown";

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
