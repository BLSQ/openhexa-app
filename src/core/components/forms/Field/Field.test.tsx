import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Input from "../Input";
import Field from "./Field";

describe("Field", () => {
  it("renders", async () => {
    const { container } = render(
      <Field name="field" label={"Field"}>
        <Input name="field" value="" onChange={() => {}} />
      </Field>,
    );

    expect(container).toMatchSnapshot();
  });

  it("renders a input if no child is given", async () => {
    const onChange = jest.fn();
    const { container } = render(
      <Field
        name="field"
        label={"Field"}
        onChange={onChange}
        value={"Value"}
      />,
    );

    expect(screen.getByDisplayValue("Value")).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });

  it("displays a question mark if help is provided", () => {
    render(
      <Field name="field" label={"Field"} help="Help">
        <span>Hey</span>
      </Field>,
    );
    expect(screen.getByTestId("help")).toBeInTheDocument();
  });
});
