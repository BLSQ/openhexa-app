import { faker } from "@faker-js/faker";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import router from "next/router";
import {
  CreateWorkspaceDocument,
  useCreateWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";
import CreateWorkspaceDialog from "./CreateWorkspaceDialog";

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useCreateWorkspaceMutation: jest.fn().mockReturnValue([]),
}));

const useCreateWorkspaceMutationMock = useCreateWorkspaceMutation as jest.Mock;

describe("CreateWorkspaceDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useCreateWorkspaceMutationMock.mockClear();
  });

  it("is not displayed ", async () => {
    const { container } = render(
      <CreateWorkspaceDialog open={false} onClose={() => {}} />,
    );
    const dialog = await screen.queryByRole("dialog");
    expect(dialog).not.toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("is displayed when open is true", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <CreateWorkspaceDialog open onClose={() => {}} />
      </TestApp>,
    );

    const dialog = screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("creates a new workspace ", async () => {
    const createWorkspace = jest.fn();
    useCreateWorkspaceMutationMock.mockReturnValue([createWorkspace]);
    const user = userEvent.setup();

    const { container } = render(
      <TestApp>
        <CreateWorkspaceDialog open onClose={() => {}} />
      </TestApp>,
    );

    const createButton = screen.getByRole("button", { name: "Create" });
    await user.click(createButton);
    expect(createWorkspace).not.toHaveBeenCalled();

    const workspaceName = screen.getByTestId("name");
    await user.type(workspaceName, "Test Burundi");
    await user.click(createButton);

    expect(createWorkspace).toHaveBeenCalled();
    expect(createWorkspace).toHaveBeenCalledWith({
      variables: {
        input: {
          name: "Test Burundi",
          countries: undefined,
          loadSampleData: false,
        },
      },
    });
  });

  it("redirects to the new workspace ", async () => {
    const { useCreateWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated",
    );
    useCreateWorkspaceMutationMock.mockImplementation(
      useCreateWorkspaceMutation,
    );
    const pushSpy = jest.spyOn(router, "push");

    const user = userEvent.setup();
    const workspace = {
      slug: faker.string.uuid(),
      name: "Workspace's name",
      description: faker.lorem.lines(),
      countries: [],
    };
    const mocks = [
      {
        request: {
          query: CreateWorkspaceDocument,
          variables: {
            input: {
              name: "Test",
              countries: [],
            },
          },
        },
        result: {
          data: {
            createWorkspace: {
              success: true,
              workspace,
              errors: [],
            },
          },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <CreateWorkspaceDialog open onClose={() => {}} />
      </TestApp>,
    );
    expect(useCreateWorkspaceMutationMock).toHaveBeenCalled();

    const createButton = screen.getByRole("button", { name: "Create" });
    const workspaceName = await screen.getByTestId("name");
    await user.type(workspaceName, "Test");
    await user.click(createButton);

    waitFor(() => {
      expect(pushSpy).toHaveBeenCalledWith({
        pathname: "/workspaces/[slug]",
        query: { slug: workspace.slug },
      });
    });
  });
});
