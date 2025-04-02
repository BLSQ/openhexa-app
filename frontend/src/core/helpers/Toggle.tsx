import useToggle from "core/hooks/useToggle";
import { ReactNode } from "react";

type Props = {
  defaultIsToggled?: boolean;
  children: (props: {
    isToggled: boolean;
    toggle: () => void;
    setTrue: () => void;
    setFalse: () => void;
  }) => ReactNode;
};

const Toggle = (props: Props) => {
  const { children, defaultIsToggled = false } = props;
  const [isToggled, { toggle, setTrue, setFalse }] =
    useToggle(defaultIsToggled);

  return (
    <>
      {children({
        isToggled,
        toggle,
        setTrue,
        setFalse,
      })}
    </>
  );
};

export default Toggle;
