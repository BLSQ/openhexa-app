import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { toast } from "react-toastify";
import PublicFileLinkButton from "./PublicFileLinkButton";
import PublicFilesSettings from "./PublicFilesSettings";
import {
  getPublicFileUrl,
  isInPublicFolder,
  isPublicFolder,
} from "./publicFiles";

const updateWorkspace = jest.fn();

jest.mock("workspaces/graphql/mutations.generated", () => ({
  useUpdateWorkspaceMutation: () => [updateWorkspace, { loading: false }],
}));

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

const BASE_URL = "https://app.openhexa.test/files/public/demo/";

const workspace = (overrides = {}) => ({
  __typename: "Workspace" as const,
  slug: "demo",
  publicFilesEnabled: false,
  publicFilesUrl: BASE_URL,
  permissions: {
    __typename: "WorkspacePermissions" as const,
    managePublicFiles: true,
  },
  ...overrides,
});

describe("publicFiles helpers", () => {
  it("recognises the public folder with or without its trailing slash", () => {
    expect(isPublicFolder("public/")).toBe(true);
    expect(isPublicFolder("public")).toBe(true);
    expect(isPublicFolder("publicity/")).toBe(false);
    expect(isPublicFolder("data/public/")).toBe(false);
  });

  it("recognises keys inside the public folder", () => {
    expect(isInPublicFolder("public/data.json")).toBe(true);
    expect(isInPublicFolder("public/tiles/")).toBe(true);
    expect(isInPublicFolder("public")).toBe(false);
    expect(isInPublicFolder("publicity/data.json")).toBe(false);
  });

  it("builds the public URL, escaping each segment but keeping the slashes", () => {
    expect(getPublicFileUrl(BASE_URL, "public/tiles/my map.pmtiles")).toBe(
      `${BASE_URL}public/tiles/my%20map.pmtiles`,
    );
  });
});

describe("PublicFileLinkButton", () => {
  it("copies the link to the clipboard", async () => {
    const writeText = jest.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    render(<PublicFileLinkButton url={`${BASE_URL}public/data.json`} />);
    fireEvent.click(screen.getByTitle("Copy the public link"));

    await waitFor(() =>
      expect(writeText).toHaveBeenCalledWith(`${BASE_URL}public/data.json`),
    );
    expect(toast.success).toHaveBeenCalledWith("Public link copied");
  });
});

describe("PublicFilesSettings", () => {
  beforeEach(() => {
    updateWorkspace.mockReset();
    updateWorkspace.mockResolvedValue({
      data: { updateWorkspace: { success: true } },
    });
  });

  it("lets an organization admin enable public files", async () => {
    render(<PublicFilesSettings workspace={workspace()} />);

    fireEvent.click(screen.getByRole("switch"));

    await waitFor(() =>
      expect(updateWorkspace).toHaveBeenCalledWith({
        variables: { input: { slug: "demo", publicFilesEnabled: true } },
      }),
    );
    expect(screen.queryByText(BASE_URL)).not.toBeInTheDocument();
  });

  it("shows the base URL once enabled", () => {
    render(
      <PublicFilesSettings
        workspace={workspace({ publicFilesEnabled: true })}
      />,
    );

    expect(screen.getByText(BASE_URL)).toBeInTheDocument();
    expect(screen.getByRole("switch")).toBeChecked();
  });

  it("is read-only for members who cannot manage public files", () => {
    render(
      <PublicFilesSettings
        workspace={workspace({
          permissions: {
            __typename: "WorkspacePermissions",
            managePublicFiles: false,
          },
        })}
      />,
    );

    expect(screen.getByRole("switch")).toBeDisabled();
    expect(
      screen.getByText(
        "Only the administrators and owners of the organization can change this setting.",
      ),
    ).toBeInTheDocument();
  });

  it("reports a failed update", async () => {
    updateWorkspace.mockResolvedValue({
      data: { updateWorkspace: { success: false } },
    });
    render(<PublicFilesSettings workspace={workspace()} />);

    fireEvent.click(screen.getByRole("switch"));

    await waitFor(() =>
      expect(toast.error).toHaveBeenCalledWith(
        "The public files setting could not be updated",
      ),
    );
  });
});
