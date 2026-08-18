import { MockedResponse } from "@apollo/client/testing";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { GenerateWorkspaceTokenDocument } from "workspaces/graphql/mutations.generated";
import WorkspaceAccessTokenField from "./WorkspaceAccessTokenField";

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

describe("WorkspaceAccessTokenField", () => {
  it("shows the whole token in a field once asked for", async () => {
    const user = userEvent.setup();
    render(
      <TestApp mocks={[buildMock()]}>
        <WorkspaceAccessTokenField workspaceSlug="my-workspace" canGenerate />
      </TestApp>,
    );

    // Nothing is masked here: the field has no other content to reveal
    expect(screen.queryByText("*********")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Show" }));
    expect(await screen.findByDisplayValue(TOKEN)).toBeInTheDocument();

    // Unlike the table cell, the dialog keeps the token in view: it is open to
    // hand it over, and reopening it starts from a hidden token again.
    expect(
      screen.queryByRole("button", { name: "Hide" }),
    ).not.toBeInTheDocument();
  });

  it("offers to copy the revealed token", async () => {
    const user = userEvent.setup();
    render(
      <TestApp mocks={[buildMock()]}>
        <WorkspaceAccessTokenField workspaceSlug="my-workspace" canGenerate />
      </TestApp>,
    );

    await user.click(screen.getByRole("button", { name: "Show" }));
    await screen.findByDisplayValue(TOKEN);

    expect(screen.getByRole("button", { name: "Copy" })).toBeInTheDocument();
  });

  it("does not offer to reveal a token without the permission", () => {
    render(
      <TestApp mocks={[]}>
        <WorkspaceAccessTokenField
          workspaceSlug="my-workspace"
          canGenerate={false}
        />
      </TestApp>,
    );

    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    // No role is shown near the field, so the message says why as well
    expect(
      screen.getByText(
        "Viewers cannot generate tokens. Ask a workspace admin for an editor role.",
      ),
    ).toBeInTheDocument();
  });
});
