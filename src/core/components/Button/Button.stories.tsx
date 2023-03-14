import { DocumentArrowDownIcon } from "@heroicons/react/24/outline";
import { Story } from "@ladle/react";

import ButtonComponent, { ButtonProps } from "./Button";

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
    <DocumentArrowDownIcon className="h-4" />
  ) : undefined;
  return (
    <ButtonComponent size={size} variant={variant} leadingIcon={leadingIcon}>
      {children}
    </ButtonComponent>
  );
};

Button.storyName = "default";
Button.args = {
  children: "Hello world",
  leading: false,
};
Button.argTypes = {
  variant: {
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

export const ButtonSnapshot: Story = () => (
  <div className="space-y-6">
    {ButtonComponent.Variants.map((variant) => (
      <div key={variant} className="flex items-center gap-4">
        {ButtonComponent.Sizes.map((size) => (
          <ButtonComponent key={size} variant={variant} size={size}>
            {variant}
          </ButtonComponent>
        ))}
      </div>
    ))}
  </div>
);
ButtonSnapshot.storyName = "Snapshot";
ButtonSnapshot.meta = {
  snapshot: true,
};

const defaults = {
  title: "UI / Button",
};

export default defaults;
