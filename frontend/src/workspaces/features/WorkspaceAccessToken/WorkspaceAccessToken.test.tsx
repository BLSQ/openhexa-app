import { MockedResponse } from "@apollo/client/testing";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { GenerateWorkspaceTokenDocument } from "workspaces/graphql/mutations.generated";
import WorkspaceAccessToken from "./WorkspaceAccessToken";

const TOKEN = "signed-access-token";

const buildMock = (): MockedResponse => ({
  request: {
    query: GenerateWorkspaceTokenDocument,
    variables: { input: { slug: "my-workspace" } },
  },
  result: {
    data: {
      generateWorkspaceToken: {
        __typename: "GenerateWorkspaceTokenResult",
        success: true,
        errors: [],
        token: TOKEN,
      },
    },
  },
});

describe("WorkspaceAccessToken", () => {
  it("does not fetch the token until the user asks for it", async () => {
    const user = userEvent.setup();
    render(
      <TestApp mocks={[buildMock()]}>
        <WorkspaceAccessToken workspaceSlug="my-workspace" canGenerate />
      </TestApp>,
    );

    expect(screen.queryByDisplayValue(TOKEN)).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Show" }));

    await waitFor(() => {
      expect(screen.getByDisplayValue(TOKEN)).toBeInTheDocument();
    });
  });

  it("flags a token that will expire, before and after revealing it", async () => {
    const user = userEvent.setup();
    render(
      <TestApp mocks={[buildMock()]}>
        <WorkspaceAccessToken
          workspaceSlug="my-workspace"
          canGenerate
          temporary
        />
      </TestApp>,
    );

    expect(screen.getByText("Temporary")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Show" }));

    await waitFor(() => {
      expect(screen.getByDisplayValue(TOKEN)).toBeInTheDocument();
    });
    expect(screen.getByText("Temporary")).toBeInTheDocument();
  });

  it("does not flag a membership token as temporary", () => {
    render(
      <TestApp mocks={[]}>
        <WorkspaceAccessToken workspaceSlug="my-workspace" canGenerate />
      </TestApp>,
    );

    expect(screen.queryByText("Temporary")).not.toBeInTheDocument();
  });

  it("does not offer to reveal a token without the permission", () => {
    render(
      <TestApp mocks={[]}>
        <WorkspaceAccessToken
          workspaceSlug="my-workspace"
          canGenerate={false}
        />
      </TestApp>,
    );

    expect(
      screen.queryByRole("button", { name: "Show" }),
    ).not.toBeInTheDocument();
    expect(screen.getByText("Not available for viewers")).toBeInTheDocument();
  });
});
