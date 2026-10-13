import { fireEvent, render, screen } from "@testing-library/react";
import { PipelineVisibility } from "graphql/types";
import PipelineVisibilityPicker from "./PipelineVisibilityPicker";

// Each card's accessible name is its label followed by its description.
const radio = (label: string) =>
  screen.getByRole("radio", { name: new RegExp(`^${label}`) });

describe("PipelineVisibilityPicker", () => {
  it("shows both visibilities and reports a selection", () => {
    const onChange = jest.fn();
    render(
      <PipelineVisibilityPicker
        value={PipelineVisibility.Workspace}
        onChange={onChange}
        canPublish
      />,
    );

    expect(screen.getAllByRole("radio")).toHaveLength(2);
    expect(radio("Workspace")).toBeChecked();

    fireEvent.click(radio("Public"));
    expect(onChange).toHaveBeenCalledWith(PipelineVisibility.Public);
  });

  it("keeps the public option out of reach of non organization admins", () => {
    const onChange = jest.fn();
    render(
      <PipelineVisibilityPicker
        value={PipelineVisibility.Workspace}
        onChange={onChange}
        canPublish={false}
      />,
    );

    expect(radio("Public")).toBeDisabled();
    expect(
      screen.getByText(
        "Only organization admins and owners can make a pipeline public.",
      ),
    ).toBeInTheDocument();

    fireEvent.click(radio("Public"));
    expect(onChange).not.toHaveBeenCalled();
  });

  it("lets anyone who can edit take a public pipeline back", () => {
    const onChange = jest.fn();
    render(
      <PipelineVisibilityPicker
        value={PipelineVisibility.Public}
        onChange={onChange}
        canPublish={false}
      />,
    );

    expect(radio("Public")).toBeChecked();
    expect(radio("Public")).toBeEnabled();
    fireEvent.click(radio("Workspace"));
    expect(onChange).toHaveBeenCalledWith(PipelineVisibility.Workspace);
  });

  it("disables every option when disabled", () => {
    render(
      <PipelineVisibilityPicker
        value={PipelineVisibility.Workspace}
        onChange={jest.fn()}
        canPublish
        disabled
      />,
    );

    ["Workspace", "Public"].forEach((label) => {
      expect(radio(label)).toBeDisabled();
    });
  });
});
