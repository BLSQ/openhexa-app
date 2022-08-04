import { Story } from "@ladle/react";
import { DocumentDownloadIcon } from "@heroicons/react/outline";

import ButtonComponent, { ButtonProps } from "./components/Button";

interface ButtonStoryProps extends ButtonProps {
  leading: boolean;
}

export const Button: Story<ButtonStoryProps> = ({
  children,
  variant,
  size,
  leading,
}) => {
  const leadingIcon = leading ? (
    <DocumentDownloadIcon className="h-4" />
  ) : undefined;
  return (
    <ButtonComponent size={size} variant={variant} leadingIcon={leadingIcon}>
      {children}
    </ButtonComponent>
  );
};

Button.args = {
  children: "Hello world",
  leading: false,
};
Button.argTypes = {
  variants: {
    options: ButtonComponent.Variants,
    control: { type: "radio" },
    defaultValue: "primary",
  },
  size: {
    options: ButtonComponent.Sizes,
    control: { type: "select" },
    defaultValue: "md",
  },
};

const defaults = {
  title: "To review / Core",
};
export default defaults;
