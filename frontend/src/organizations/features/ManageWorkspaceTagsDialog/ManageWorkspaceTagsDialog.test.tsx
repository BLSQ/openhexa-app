import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { SetWorkspaceTagsError } from "graphql/types";
import { toast } from "react-toastify";
import { v4 } from "uuid";
import ManageWorkspaceTagsDialog from "./ManageWorkspaceTagsDialog";
import { useSetWorkspaceTagsMutation } from "./ManageWorkspaceTagsDialog.generated";

jest.mock("./ManageWorkspaceTagsDialog.generated", () => ({
  ...jest.requireActual("./ManageWorkspaceTagsDialog.generated"),
  useSetWorkspaceTagsMutation: jest.fn(),
}));

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("core/hooks/useCacheKey", () => ({
  __esModule: true,
  default: () => jest.fn(),
}));

// The description interpolates the workspace name, so the mock resolves {{...}}
// placeholders instead of returning the raw key.
jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, options?: Record<string, string>) =>
      options
        ? key.replace(/{{(\w+)}}/g, (match, name) => options[name] ?? match)
        : key,
  }),
}));

const ORGANIZATION_ID = v4();

const WORKSPACE = {
  slug: "test-workspace",
  name: "Test Workspace",
  tags: [{ name: "covid" }],
};

const AVAILABLE_TAGS = ["analytics", "covid", "malaria"];

const useSetWorkspaceTagsMutationMock =
  useSetWorkspaceTagsMutation as unknown as jest.Mock;

const renderDialog = (onClose: jest.Mock) =>
  render(
    <TestApp mocks={[]}>
      <ManageWorkspaceTagsDialog
        open={true}
        onClose={onClose}
        workspace={WORKSPACE}
        organizationId={ORGANIZATION_ID}
        availableTags={AVAILABLE_TAGS}
      />
    </TestApp>,
  );

const mockMutationResult = (result: any) => {
  const mutate = jest.fn().mockResolvedValue(result);
  useSetWorkspaceTagsMutationMock.mockReturnValue([mutate, {}]);
  return mutate;
};

const mockFailure = (errors: SetWorkspaceTagsError[]) =>
  mockMutationResult({
    data: { setWorkspaceTags: { success: false, errors } },
  });

describe("ManageWorkspaceTagsDialog", () => {
  const onClose = jest.fn();

  beforeEach(() => {
    mockMutationResult({
      data: {
        setWorkspaceTags: {
          success: true,
          errors: [],
          workspace: { slug: WORKSPACE.slug, tags: [] },
        },
      },
    });
  });

  it("displays the workspace name and the normalization hint", () => {
    renderDialog(onClose);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Manage tags")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Tag Test Workspace to organize and filter the workspaces of your organization.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        'Tags are normalized to lowercase words separated by hyphens, so "Project Alpha" is saved as "project-alpha".',
      ),
    ).toBeInTheDocument();
  });

  it("pre-selects the tags already assigned to the workspace", () => {
    renderDialog(onClose);

    expect(screen.getByText("covid")).toBeInTheDocument();
  });

  it("saves the unchanged selection", async () => {
    const user = userEvent.setup();
    const mutate = mockMutationResult({
      data: {
        setWorkspaceTags: {
          success: true,
          errors: [],
          workspace: { slug: WORKSPACE.slug, tags: [{ name: "covid" }] },
        },
      },
    });

    renderDialog(onClose);
    await user.click(screen.getByText("Save"));

    await waitFor(() => {
      expect(mutate).toHaveBeenCalledWith({
        variables: { input: { slug: WORKSPACE.slug, tags: ["covid"] } },
      });
    });

    expect(toast.success).toHaveBeenCalledWith("Tags updated!");
    expect(onClose).toHaveBeenCalled();
  });

  it("saves a tag picked from the available ones", async () => {
    const user = userEvent.setup();
    const mutate = mockMutationResult({
      data: {
        setWorkspaceTags: { success: true, errors: [], workspace: null },
      },
    });

    renderDialog(onClose);

    await user.click(screen.getByTestId("combobox-button"));
    await waitFor(() => {
      expect(screen.getByTestId("combobox-options")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("option", { name: "malaria" }));

    await user.click(screen.getByText("Save"));

    await waitFor(() => {
      expect(mutate).toHaveBeenCalledWith({
        variables: {
          input: { slug: WORKSPACE.slug, tags: ["covid", "malaria"] },
        },
      });
    });
  });

  it("sends a freshly created tag as typed, leaving normalization to the backend", async () => {
    const user = userEvent.setup();
    const mutate = mockMutationResult({
      data: {
        setWorkspaceTags: { success: true, errors: [], workspace: null },
      },
    });

    renderDialog(onClose);

    await user.type(screen.getByTestId("combobox-input"), "Project Alpha");
    await user.click(screen.getByText('Create tag "Project Alpha"'));

    await user.click(screen.getByText("Save"));

    await waitFor(() => {
      expect(mutate).toHaveBeenCalledWith({
        variables: {
          input: { slug: WORKSPACE.slug, tags: ["covid", "Project Alpha"] },
        },
      });
    });
  });

  it("reports a permission denial and keeps the dialog open", async () => {
    const user = userEvent.setup();
    mockFailure([SetWorkspaceTagsError.PermissionDenied]);

    renderDialog(onClose);
    await user.click(screen.getByText("Save"));

    await waitFor(() => {
      expect(
        screen.getByText("You are not authorized to perform this action"),
      ).toBeInTheDocument();
    });

    expect(toast.success).not.toHaveBeenCalled();
    expect(onClose).not.toHaveBeenCalled();
  });

  it("reports an unusable tag", async () => {
    const user = userEvent.setup();
    mockFailure([SetWorkspaceTagsError.InvalidTag]);

    renderDialog(onClose);
    await user.click(screen.getByText("Save"));

    await waitFor(() => {
      expect(
        screen.getByText(
          "One of the tags contains no letters or numbers to use.",
        ),
      ).toBeInTheDocument();
    });

    expect(onClose).not.toHaveBeenCalled();
  });

  it("reports a missing workspace", async () => {
    const user = userEvent.setup();
    mockFailure([SetWorkspaceTagsError.NotFound]);

    renderDialog(onClose);
    await user.click(screen.getByText("Save"));

    await waitFor(() => {
      expect(screen.getByText("Workspace not found")).toBeInTheDocument();
    });

    expect(onClose).not.toHaveBeenCalled();
  });

  it("falls back to a generic message on an unknown failure", async () => {
    const user = userEvent.setup();
    mockFailure([]);

    renderDialog(onClose);
    await user.click(screen.getByText("Save"));

    await waitFor(() => {
      expect(
        screen.getByText("Failed to update the tags of the workspace"),
      ).toBeInTheDocument();
    });

    expect(onClose).not.toHaveBeenCalled();
  });

  it("closes without saving when cancelled", async () => {
    const user = userEvent.setup();
    const mutate = mockMutationResult({
      data: {
        setWorkspaceTags: { success: true, errors: [], workspace: null },
      },
    });

    renderDialog(onClose);
    await user.click(screen.getByText("Cancel"));

    expect(onClose).toHaveBeenCalled();
    expect(mutate).not.toHaveBeenCalled();
  });
});
