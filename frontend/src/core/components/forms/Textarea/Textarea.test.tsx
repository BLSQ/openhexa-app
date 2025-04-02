import Textarea from "./Textarea";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

describe("Textarea", () => {
  it("renders", async () => {
    const { container } = render(
      <Textarea value={"this is a textarea"} onChange={() => {}} />,
    );

    expect(container).toMatchSnapshot();
  });

  it("calls onChange when user types in the textarea", async () => {
    const onChange = jest.fn();
    const { container } = render(
      <Textarea
        data-testid="textarea"
        value={"this is a textarea"}
        onChange={onChange}
      />,
    );
    const textarea = screen.getByTestId("textarea");

    await userEvent.type(textarea, "TEXT");

    expect(onChange).toHaveBeenCalled();
  });
});
