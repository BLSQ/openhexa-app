import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import ParameterField from "./ParameterField";

describe("ParameterField", () => {
  it("renders a switch for boolean parameter", async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();
    const param = {
      code: "is_ok",
      name: "is_ok",
      type: "bool",
      default: false,
      required: false,
      choices: null,
      multiple: false,
    };
    const form = {};

    render(
      <ParameterField
        parameter={param}
        value={param.default}
        onChange={onChange}
        form={form}
      />,
    );

    const switchButton = screen.getByRole("switch");
    expect(switchButton).toBeInTheDocument();
    expect(switchButton.getAttribute("aria-checked")).toBe(
      param.default.toString(),
    );
    await user.click(switchButton);

    expect(onChange).toHaveBeenCalledWith(!param.default);
  });

  it("renders number input for int param", async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    const param = {
      code: "int_param",
      name: "int",
      type: "int",
      default: 0,
      required: false,
      choices: null,
      multiple: false,
      connection: null,
      widget: null,
    };
    const form = {};
    render(
      <ParameterField
        parameter={param}
        value={param.default}
        onChange={onChange}
        form={form}
      />,
    );

    const input = screen.getByTestId(`${param.code}-input`);

    await user.type(input, "This will not work");
    expect(onChange).not.toHaveBeenCalled();

    await user.type(input, "1");
    expect(onChange).toHaveBeenCalledWith("1");
  });

  it("renders for multiple int param", async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    const param = {
      code: "int_param",
      name: "int",
      type: "int",
      default: "",
      required: false,
      choices: null,
      multiple: true,
      connection: null,
      widget: null,
    };
    const form = {};

    const { debug } = render(
      <ParameterField
        parameter={param}
        value={param.default}
        onChange={onChange}
        form={form}
      />,
    );

    const input = screen.getByTestId(`${param.code}-textarea`);

    input.focus();
    user.paste("123\n456");
    expect(onChange).toHaveBeenLastCalledWith(["123", "456"]);
  });

  it("renders an input of type string", async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    const param = {
      code: "str_param",
      name: "str_param",
      type: "str",
      default: 0,
      required: false,
      choices: null,
      multiple: false,
      connection: null,
      widget: null,
    };
    const form = {};

    render(
      <ParameterField
        parameter={param}
        value={param.default}
        onChange={onChange}
        form={form}
      />,
    );

    const input = screen.getByTestId(`${param.code}-input`);
    await user.type(input, "This will work");

    expect(onChange).toHaveBeenCalled();
  });

  it("renders a select if param have choices", async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    const param = {
      code: "choice_param",
      name: "choice__param",
      type: "int",
      default: 1,
      required: false,
      choices: [1, 2, 3],
      multiple: false,
      connection: null,
      widget: null,
    };
    const form = {};

    render(
      <ParameterField
        parameter={param}
        value={param.default}
        onChange={onChange}
        form={form}
      />,
    );

    await user.click(await screen.findByTestId("combobox-button"));
    await user.click(await screen.findByText("2"));

    expect(onChange).toHaveBeenCalledWith("2");
  });

  it("renders a select if param have choices and multiple", async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    const param = {
      code: "choice_param",
      name: "choice__param",
      type: "int",
      default: null,
      required: false,
      widget: null,
      connection: null,
      choices: [1, 2, 3],
      multiple: true,
    };
    const form = {};

    render(
      <ParameterField
        parameter={param}
        value={param.default}
        onChange={onChange}
        form={form}
      />,
    );

    await user.click(await screen.findByTestId("combobox-button"));
    await user.click(await screen.findByText("2"));

    expect(onChange).toHaveBeenCalledWith(["2"]);
  });

  it("renders a select if param have choices and multiple with default value", async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    const param = {
      code: "choice_param",
      name: "choice__param",
      type: "str",
      default: "a",
      required: false,
      choices: ["a", "b", "c"],
      multiple: true,
      widget: null,
      connection: null,
    };
    const form = {};
    render(
      <ParameterField
        parameter={param}
        value={param.default}
        onChange={onChange}
        form={form}
      />,
    );

    await user.click(await screen.findByTestId("combobox-button"));
    await user.click(await screen.findByText("b"));

    expect(onChange).toHaveBeenCalledWith(["a", "b"]);
  });

  it("renders a textarea for param multiple", async () => {
    const onChange = jest.fn();
    const param = {
      code: "multi_param",
      name: "multi_param",
      type: "str",
      default: "",
      required: false,
      choices: null,
      multiple: true,
      widget: null,
      connection: null,
    };
    const form = {};
    const user = userEvent.setup();

    render(
      <ParameterField
        parameter={param}
        value={param.default}
        onChange={onChange}
        form={form}
      />,
    );

    const textarea = screen.getByTestId(`${param.code}-textarea`);
    await user.type(textarea, "TEXT");
    expect(onChange).toHaveBeenCalled();
  });
});
