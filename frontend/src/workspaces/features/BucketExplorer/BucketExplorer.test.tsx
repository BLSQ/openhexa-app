import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { BucketObjectType } from "graphql/types";
import mockRouter from "next-router-mock";
import { toast } from "react-toastify";
import { createBucketFolder } from "workspaces/helpers/bucket";
import BucketExplorer, { getPublicFileUrl } from "./BucketExplorer";

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("workspaces/helpers/bucket", () => ({
  ...jest.requireActual("workspaces/helpers/bucket"),
  createBucketFolder: jest.fn(),
}));

const PUBLIC_FILES_URL = "http://localhost:8000/files/my-ws/public/";

const buildObject = (key: string, type: BucketObjectType) => ({
  __typename: "BucketObject" as const,
  key,
  name: key.replace(/\/$/, "").split("/").pop()!,
  path: `bucket/${key}`,
  size: type === BucketObjectType.File ? 12 : null,
  updatedAt: "2026-11-04T10:00:00Z",
  type,
});

type RenderOptions = {
  publicFiles?: { url: string | null; folderExists: boolean } | null;
  createObject?: boolean;
  managePublicFiles?: boolean;
  prefix?: string | null;
};

const renderExplorer = (
  publicFilesUrl: string | null,
  items: any[],
  {
    publicFiles = { url: publicFilesUrl, folderExists: true },
    createObject = true,
    managePublicFiles = true,
    prefix = null,
  }: RenderOptions = {},
) =>
  render(
    <TestApp>
      <BucketExplorer
        workspace={{
          __typename: "Workspace",
          slug: "my-ws",
          publicFiles: publicFiles && {
            __typename: "WorkspacePublicFiles",
            ...publicFiles,
          },
          permissions: {
            __typename: "WorkspacePermissions",
            deleteObject: true,
            createObject,
            managePublicFiles,
          },
        }}
        objects={{
          __typename: "BucketObjectPage",
          hasNextPage: false,
          hasPreviousPage: false,
          pageNumber: 1,
          items,
        }}
        prefix={prefix}
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
  it("marks the public folder as shared only when public files are enabled", () => {
    const items = [
      buildObject("public/", BucketObjectType.Directory),
      buildObject("data.csv", BucketObjectType.File),
    ];
    const { unmount } = renderExplorer(null, items);
    expect(screen.queryByLabelText("Shared publicly")).not.toBeInTheDocument();
    unmount();

    renderExplorer(PUBLIC_FILES_URL, items);
    expect(screen.getByLabelText("Shared publicly")).toBeInTheDocument();
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

describe("BucketExplorer public folder placeholder", () => {
  const items = [buildObject("data.csv", BucketObjectType.File)];

  it("is hidden when the instance does not offer public files", () => {
    renderExplorer(null, items, { publicFiles: null });
    expect(screen.queryByText("public")).not.toBeInTheDocument();
  });

  it("is hidden once the public folder exists", () => {
    renderExplorer(null, items, {
      publicFiles: { url: null, folderExists: true },
    });
    expect(screen.queryByText("public")).not.toBeInTheDocument();
  });

  it("is hidden outside of the root folder", () => {
    renderExplorer(null, items, {
      publicFiles: { url: null, folderExists: false },
      prefix: "data/",
    });
    expect(screen.queryByText("public")).not.toBeInTheDocument();
  });

  it("links admins to the settings while public files are disabled", () => {
    renderExplorer(null, items, {
      publicFiles: { url: null, folderExists: false },
    });
    expect(screen.getByText("public")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Enable public files" }),
    ).toHaveAttribute("href", "/workspaces/my-ws/settings");
  });

  it("tells editors to ask an admin while public files are disabled", () => {
    renderExplorer(null, items, {
      publicFiles: { url: null, folderExists: false },
      managePublicFiles: false,
    });
    expect(
      screen.getByText("Ask a workspace admin to enable public files"),
    ).toBeInTheDocument();
  });

  it("is hidden for viewers", () => {
    renderExplorer(null, items, {
      publicFiles: { url: null, folderExists: false },
      managePublicFiles: false,
      createObject: false,
    });
    expect(screen.queryByText("public")).not.toBeInTheDocument();
  });

  it("creates the public folder once public files are enabled", async () => {
    const user = userEvent.setup();
    (createBucketFolder as jest.Mock).mockResolvedValue({ key: "public/" });
    renderExplorer(PUBLIC_FILES_URL, items, {
      publicFiles: { url: PUBLIC_FILES_URL, folderExists: false },
      managePublicFiles: false,
    });

    await user.click(screen.getByRole("button", { name: "Create folder" }));

    expect(createBucketFolder).toHaveBeenCalledWith("my-ws", "public");
    await waitFor(() =>
      expect(mockRouter.asPath).toBe("/workspaces/my-ws/files/public"),
    );
  });
});
