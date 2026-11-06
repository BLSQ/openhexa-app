import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { BucketObjectType } from "graphql/types";
import { toast } from "react-toastify";
import BucketExplorer, { getPublicFileUrl } from "./BucketExplorer";

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

const PUBLIC_FILES_URL = "http://localhost:8000/files/public/my-ws/";

const buildObject = (key: string, type: BucketObjectType) => ({
  __typename: "BucketObject" as const,
  key,
  name: key.replace(/\/$/, "").split("/").pop()!,
  path: `bucket/${key}`,
  size: type === BucketObjectType.File ? 12 : null,
  updatedAt: "2026-11-04T10:00:00Z",
  type,
});

const renderExplorer = (publicFilesUrl: string | null, items: any[]) =>
  render(
    <TestApp>
      <BucketExplorer
        workspace={{
          __typename: "Workspace",
          slug: "my-ws",
          publicFilesUrl,
          permissions: {
            __typename: "WorkspacePermissions",
            deleteObject: true,
          },
        }}
        objects={{
          __typename: "BucketObjectPage",
          hasNextPage: false,
          hasPreviousPage: false,
          pageNumber: 1,
          items,
        }}
        prefix={null}
        perPage={20}
        onChangePage={jest.fn()}
      />
    </TestApp>,
  );

describe("getPublicFileUrl", () => {
  it("builds the URL relative to the public folder and encodes each segment", () => {
    expect(
      getPublicFileUrl(PUBLIC_FILES_URL, "public/maps/my tiles#1.pmtiles"),
    ).toBe(`${PUBLIC_FILES_URL}maps/my%20tiles%231.pmtiles`);
  });
});

describe("BucketExplorer public files", () => {
  it("shows the public badge and copy link only when public files are enabled", () => {
    const items = [
      buildObject("public/", BucketObjectType.Directory),
      buildObject("data.csv", BucketObjectType.File),
    ];
    const { unmount } = renderExplorer(null, items);
    expect(screen.queryByText("Public")).not.toBeInTheDocument();
    unmount();

    renderExplorer(PUBLIC_FILES_URL, items);
    expect(screen.getByText("Public")).toBeInTheDocument();
    expect(screen.queryByTitle("Copy public link")).not.toBeInTheDocument();
  });

  it("copies the public link of files in the public folder", async () => {
    const user = userEvent.setup();
    const writeText = jest
      .spyOn(navigator.clipboard, "writeText")
      .mockResolvedValue(undefined);
    renderExplorer(PUBLIC_FILES_URL, [
      buildObject("public/data.csv", BucketObjectType.File),
    ]);

    await user.click(screen.getByTitle("Copy public link"));

    await waitFor(() =>
      expect(writeText).toHaveBeenCalledWith(`${PUBLIC_FILES_URL}data.csv`),
    );
  });

  it("tells the user when the link could not be copied", async () => {
    const user = userEvent.setup();
    jest
      .spyOn(navigator.clipboard, "writeText")
      .mockRejectedValue(new Error("denied"));
    renderExplorer(PUBLIC_FILES_URL, [
      buildObject("public/data.csv", BucketObjectType.File),
    ]);

    await user.click(screen.getByTitle("Copy public link"));

    await waitFor(() =>
      expect(toast.error).toHaveBeenCalledWith(
        "The public link could not be copied to the clipboard",
      ),
    );
  });
});
