import { PlusIcon } from "@heroicons/react/24/outline";
import { render, screen, fireEvent } from "@testing-library/react";
import Button from "./Button";

describe("Button", () => {
  it("renders a Button", () => {
    render(<Button>This is a button</Button>);

    const text = screen.getByText("This is a button");
    expect(text).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>button</Button>);

    const btn = screen.getByRole("button");
    fireEvent.click(btn);

    expect(onClick).toHaveBeenCalled();
  });

  it("does not call onClick when disabled and clicked", () => {
    const onClick = jest.fn();
    render(
      <Button disabled onClick={onClick}>
        button
      </Button>,
    );

    const btn = screen.getByRole("button");
    fireEvent.click(btn);

    expect(onClick).not.toHaveBeenCalled();
  });

  it("renders all variants and all sizes of the button", () => {
    const container = render(
      <div className="space-y-6">
        {Button.Variants.map((variant) => (
          <div key={variant} className="flex items-center gap-4">
            {Button.Sizes.map((size) => (
              <Button key={size} variant={variant} size={size}>
                {variant}
              </Button>
            ))}
          </div>
        ))}
      </div>,
    );

    expect(container).toMatchSnapshot();
  });

  it("renders an icon in front of the label", () => {
    const container = render(
      <Button
        disabled
        leadingIcon={<PlusIcon className="w-4" data-testid="icon" />}
      >
        button
      </Button>,
    );

    const icon = screen.getByTestId("icon");

    expect(icon).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });

  it("accepts additional classes", () => {
    render(<Button className="font-black">Black</Button>);

    const button = screen.getByRole("button");

    expect(button).toHaveClass("font-black");
  });
});
