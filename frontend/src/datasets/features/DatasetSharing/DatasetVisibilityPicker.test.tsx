import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { updateDataset } from "datasets/helpers/dataset";
import { DatasetVisibility } from "graphql/types";
import DatasetVisibilityPicker from "./DatasetVisibilityPicker";

jest.mock("datasets/helpers/dataset", () => ({ updateDataset: jest.fn() }));
jest.mock("react-toastify", () => ({ toast: { error: jest.fn() } }));

const renderPicker = ({
  visibility = DatasetVisibility.Workspace,
  disabled = false,
} = {}) =>
  render(
    <DatasetVisibilityPicker
      disabled={disabled}
      dataset={{
        id: "dataset-id",
        slug: "my-dataset",
        publicSlug: null,
        visibility,
        permissions: { update: true, share: true },
      }}
    />,
  );

const pick = async (label: string) => {
  fireEvent.click(screen.getByRole("button", { name: "Visibility" }));
  fireEvent.click(
    await screen.findByRole("option", { name: new RegExp(`^${label}`) }),
  );
};

beforeEach(() => jest.clearAllMocks());

describe("DatasetVisibilityPicker", () => {
  it("shares with the organization straight away", async () => {
    renderPicker();
    await pick("Organization");

    await waitFor(() =>
      expect(updateDataset).toHaveBeenCalledWith("dataset-id", {
        visibility: DatasetVisibility.Organization,
        publicSlug: undefined,
      }),
    );
    expect(
      screen.queryByRole("button", { name: "Make dataset public" }),
    ).not.toBeInTheDocument();
  });

  it("asks to confirm making it public, with its public slug", async () => {
    renderPicker();
    await pick("Public");

    expect(updateDataset).not.toHaveBeenCalled();
    expect(
      await screen.findByText("Make this dataset public?"),
    ).toBeInTheDocument();
    expect(screen.getByDisplayValue("my-dataset")).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: "Make dataset public" }),
    );

    await waitFor(() =>
      expect(updateDataset).toHaveBeenCalledWith("dataset-id", {
        visibility: DatasetVisibility.Public,
        publicSlug: "my-dataset",
      }),
    );
  });

  it("asks to confirm before stopping public sharing", async () => {
    renderPicker({ visibility: DatasetVisibility.Public });
    await pick("Organization");

    expect(
      await screen.findByText("The public link will stop working."),
    ).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: "Stop sharing publicly" }),
    );

    await waitFor(() =>
      expect(updateDataset).toHaveBeenCalledWith("dataset-id", {
        visibility: DatasetVisibility.Organization,
        publicSlug: undefined,
      }),
    );
  });

  it("only shows the visibility when disabled", () => {
    renderPicker({ disabled: true });
    expect(screen.getByRole("button", { name: "Visibility" })).toBeDisabled();
    expect(screen.getByText("Private")).toBeInTheDocument();
  });

  it("shows the public link identifier of a public dataset", () => {
    render(
      <DatasetVisibilityPicker
        dataset={{
          id: "dataset-id",
          slug: "my-dataset",
          publicSlug: "malaria-cases",
          visibility: DatasetVisibility.Public,
          permissions: { update: true, share: true },
        }}
      />,
    );
    expect(screen.getByText("malaria-cases")).toBeInTheDocument();
  });
});
