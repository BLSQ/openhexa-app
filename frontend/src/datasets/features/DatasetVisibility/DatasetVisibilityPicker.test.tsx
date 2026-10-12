import { fireEvent, render, screen } from "@testing-library/react";
import { DatasetVisibility } from "graphql/types";
import DatasetVisibilityPicker from "./DatasetVisibilityPicker";

// Each card's accessible name is its label followed by its description.
const radio = (label: string) =>
  screen.getByRole("radio", { name: new RegExp(`^${label}`) });

describe("DatasetVisibilityPicker", () => {
  it("shows the three visibilities and reports a selection", () => {
    const onChange = jest.fn();
    render(
      <DatasetVisibilityPicker
        value={DatasetVisibility.Private}
        onChange={onChange}
        canMakePublic
      />,
    );

    expect(screen.getAllByRole("radio")).toHaveLength(3);
    expect(radio("Private")).toBeChecked();
    expect(radio("Public")).toBeEnabled();

    fireEvent.click(radio("Organization"));
    expect(onChange).toHaveBeenCalledWith(DatasetVisibility.Organization);

    fireEvent.click(radio("Public"));
    expect(onChange).toHaveBeenCalledWith(DatasetVisibility.Public);
  });

  it("keeps the public option out of reach of non organization admins", () => {
    const onChange = jest.fn();
    render(
      <DatasetVisibilityPicker
        value={DatasetVisibility.Organization}
        onChange={onChange}
        canMakePublic={false}
      />,
    );

    expect(radio("Public")).toBeDisabled();
    expect(radio("Private")).toBeEnabled();
    expect(
      screen.getByText(
        "Only organization admins and owners can make a dataset public.",
      ),
    ).toBeInTheDocument();

    fireEvent.click(radio("Public"));
    expect(onChange).not.toHaveBeenCalled();
  });

  it("still shows public as selected when a non admin looks at a public dataset", () => {
    render(
      <DatasetVisibilityPicker
        value={DatasetVisibility.Public}
        onChange={jest.fn()}
        canMakePublic={false}
      />,
    );

    expect(radio("Public")).toBeChecked();
    expect(radio("Public")).toBeEnabled();
  });

  it("disables every option when disabled", () => {
    render(
      <DatasetVisibilityPicker
        value={DatasetVisibility.Private}
        onChange={jest.fn()}
        canMakePublic
        disabled
      />,
    );

    ["Private", "Organization", "Public"].forEach((label) => {
      expect(radio(label)).toBeDisabled();
    });
  });
});
