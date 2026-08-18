import { MockedResponse } from "@apollo/client/testing";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { GenerateWorkspaceTokenDocument } from "workspaces/graphql/mutations.generated";
import WorkspaceAccessTokenCell from "./WorkspaceAccessTokenCell";

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

describe("WorkspaceAccessTokenCell", () => {
  it("masks the token until the user reveals it", async () => {
    const user = userEvent.setup();
    render(
      <TestApp mocks={[buildMock()]}>
        <WorkspaceAccessTokenCell workspaceSlug="my-workspace" canGenerate />
      </TestApp>,
    );

    expect(screen.getByText("*********")).toBeInTheDocument();
    expect(screen.queryByText(TOKEN)).not.toBeInTheDocument();

    await user.click(
      screen.getByRole("button", { name: "Show the access token" }),
    );
    expect(await screen.findByText(TOKEN)).toBeInTheDocument();

    // The same control hides it again, so it never moves between the two states
    await user.click(
      screen.getByRole("button", { name: "Hide the access token" }),
    );
    expect(screen.getByText("*********")).toBeInTheDocument();
  });

  it("explains a token that will expire, before and after revealing it", async () => {
    const user = userEvent.setup();
    render(
      <TestApp mocks={[buildMock()]}>
        <WorkspaceAccessTokenCell
          workspaceSlug="my-workspace"
          canGenerate
          temporary
        />
      </TestApp>,
    );

    // The flag itself is an icon; "Temporary" is its accessible name
    expect(screen.getByText("Temporary")).toBeInTheDocument();

    await user.hover(screen.getByText("Temporary"));
    expect(
      await screen.findByText(
        "You are not a direct member of this workspace, so this token is temporary: generate a new one once it expires.",
      ),
    ).toBeInTheDocument();
    await user.unhover(screen.getAllByText("Temporary")[0]);

    await user.click(
      screen.getByRole("button", { name: "Show the access token" }),
    );
    expect(await screen.findByText(TOKEN)).toBeInTheDocument();
    expect(screen.getAllByText("Temporary")).not.toHaveLength(0);
  });

  it("does not flag a membership token as temporary", () => {
    render(
      <TestApp mocks={[]}>
        <WorkspaceAccessTokenCell workspaceSlug="my-workspace" canGenerate />
      </TestApp>,
    );

    expect(screen.queryByText("Temporary")).not.toBeInTheDocument();
  });

  it("does not offer to reveal a token without the permission", () => {
    render(
      <TestApp mocks={[]}>
        <WorkspaceAccessTokenCell
          workspaceSlug="my-workspace"
          canGenerate={false}
        />
      </TestApp>,
    );

    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    // The Role column carries the "why", so the cell only points the way out
    expect(
      screen.getByText("Ask a workspace admin for an editor role."),
    ).toBeInTheDocument();
  });
});
