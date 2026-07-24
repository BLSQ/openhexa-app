import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SavedQueryParameter } from "workspaces/features/SavedQueries/savedQueryParameters";
import SavedQueryRunPanel from "./SavedQueryRunPanel";

// useTranslation is globally mocked to echo the key.

const setup = (parameters: SavedQueryParameter[]) => {
  const onRun = jest.fn();
  render(
    <SavedQueryRunPanel
      parameters={parameters}
      loading={false}
      onRun={onRun}
    />,
  );
  return { onRun };
};

describe("SavedQueryRunPanel", () => {
  it("only sends non-empty values so defaults apply on the backend", async () => {
    const { onRun } = setup([
      { name: "country", type: "string", kind: "value" },
      { name: "limit", type: "integer", kind: "value" },
    ]);

    // `country` is the only text input; `limit` (number) is a spinbutton.
    await userEvent.type(screen.getByRole("textbox"), "BE");
    // `limit` is left blank.
    await userEvent.click(
      screen.getByRole("button", { name: "Run with parameters" }),
    );

    expect(onRun).toHaveBeenCalledWith({ country: "BE" });
  });

  it("renders an allowlist as a dropdown for enum parameters", () => {
    setup([
      {
        name: "direction",
        type: "string",
        kind: "enum",
        choices: ["ASC", "DESC"],
      },
    ]);

    expect(screen.getByRole("option", { name: "ASC" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "DESC" })).toBeInTheDocument();
  });

  it("renders a true/false dropdown for boolean parameters", () => {
    const { onRun } = setup([
      { name: "active", type: "boolean", kind: "value" },
    ]);

    fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "true" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Run with parameters" }),
    );

    expect(onRun).toHaveBeenCalledWith({ active: "true" });
  });

  it("marks required parameters", () => {
    setup([{ name: "country", type: "string", kind: "value", required: true }]);

    expect(screen.getByText("country")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("required")).toBeInTheDocument();
  });
});
