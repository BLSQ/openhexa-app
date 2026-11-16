import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { updateDataset } from "datasets/helpers/dataset";
import { DatasetVisibility } from "graphql/types";
import { toast } from "react-toastify";
import DatasetShareButton from "./DatasetShareButton";

jest.mock("datasets/helpers/dataset", () => ({ updateDataset: jest.fn() }));
jest.mock("react-toastify", () => ({ toast: { error: jest.fn() } }));

const renderButton = ({
  visibility = DatasetVisibility.Workspace,
  publicSlug = null as string | null,
  update = true,
  share = true,
} = {}) =>
  render(
    <DatasetShareButton
      dataset={{
        id: "dataset-id",
        slug: "my-dataset",
        publicSlug,
        visibility,
        permissions: { update, share },
      }}
    />,
  );

const radio = (label: string) =>
  screen.getByRole("radio", { name: new RegExp(`^${label}`) });
const openAndChoose = async (label: string) => {
  fireEvent.click(screen.getByRole("button", { name: "Share" }));
  await screen.findByRole("radio", { name: /^Private/ });
  fireEvent.click(radio(label));
};
const save = () =>
  fireEvent.click(screen.getByRole("button", { name: "Save" }));

beforeEach(() => jest.clearAllMocks());

describe("DatasetShareButton", () => {
  it("is hidden without the right to update", () => {
    renderButton({ update: false });
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("shares with the organization on save", async () => {
    renderButton();
    await openAndChoose("Organization");
    expect(updateDataset).not.toHaveBeenCalled();
    save();

    await waitFor(() =>
      expect(updateDataset).toHaveBeenCalledWith("dataset-id", {
        visibility: DatasetVisibility.Organization,
        publicSlug: undefined,
      }),
    );
  });

  it("makes the dataset public with the chosen slug, defaulting to the dataset slug", async () => {
    renderButton();
    await openAndChoose("Public");

    fireEvent.change(screen.getByDisplayValue("my-dataset"), {
      target: { value: "malaria-2026" },
    });
    save();

    await waitFor(() =>
      expect(updateDataset).toHaveBeenCalledWith("dataset-id", {
        visibility: DatasetVisibility.Public,
        publicSlug: "malaria-2026",
      }),
    );
  });

  it("does not resend a public slug that is already claimed", async () => {
    renderButton({
      visibility: DatasetVisibility.Organization,
      publicSlug: "claimed",
    });
    await openAndChoose("Public");

    expect(screen.getByDisplayValue("claimed")).toBeDisabled();
    save();

    await waitFor(() =>
      expect(updateDataset).toHaveBeenCalledWith("dataset-id", {
        visibility: DatasetVisibility.Public,
        publicSlug: undefined,
      }),
    );
  });

  it("warns before stopping public sharing", async () => {
    renderButton({
      visibility: DatasetVisibility.Public,
      publicSlug: "claimed",
    });
    await openAndChoose("Private");
    expect(
      screen.getByText("The public link will stop working."),
    ).toBeInTheDocument();
  });

  it("keeps the dialog open and reports a refused public slug", async () => {
    (updateDataset as jest.Mock).mockRejectedValueOnce(
      new Error("This public link identifier is already used."),
    );
    renderButton();
    await openAndChoose("Public");
    save();

    await waitFor(() =>
      expect(toast.error).toHaveBeenCalledWith(
        "This public link identifier is already used.",
      ),
    );
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument();
  });

  it("does not offer public sharing without the share permission", async () => {
    renderButton({ share: false });
    fireEvent.click(screen.getByRole("button", { name: "Share" }));

    expect(
      await screen.findByRole("radio", { name: /^Public/ }),
    ).toBeDisabled();
    expect(
      screen.getByText(
        "Only the author, workspace admins and organization admins can make a dataset public.",
      ),
    ).toBeInTheDocument();
  });
});
