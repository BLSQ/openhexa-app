import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import mockRouter from "next-router-mock";
import { useSupersetInstancesQuery } from "webapps/graphql/queries.generated";
import CreateWebappDialog from "./CreateWebappDialog";

jest.mock("webapps/graphql/queries.generated", () => ({
  __esModule: true,
  ...jest.requireActual("webapps/graphql/queries.generated"),
  useSupersetInstancesQuery: jest.fn(),
}));

const buildWorkspace = ({
  aiEnabled = true,
  aiBudgetLimitReached = false,
} = {}) => ({
  slug: "test-workspace",
  organization: {
    id: "org-1",
    aiSettings: { enabled: aiEnabled },
    aiBudgetLimitReached,
  },
});

const mockSupersetInstances = (instances: { id: string; url: string }[]) =>
  (useSupersetInstancesQuery as jest.Mock).mockReturnValue({
    data: { supersetInstances: instances },
  });

const renderDialog = (workspace = buildWorkspace()) =>
  render(
    <TestApp>
      <CreateWebappDialog open onClose={jest.fn()} workspace={workspace} />
    </TestApp>,
  );

describe("CreateWebappDialog", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/workspaces/test-workspace/webapps");
    mockSupersetInstances([]);
  });

  it("offers every creation method", async () => {
    mockSupersetInstances([
      { id: "superset-1", url: "https://superset.example.org" },
    ]);
    renderDialog();

    expect(await screen.findByText("Create with AI")).toBeInTheDocument();
    expect(screen.getByText("From code")).toBeInTheDocument();
    expect(screen.getByText("Superset")).toBeInTheDocument();
    expect(screen.getByText("iFrame")).toBeInTheDocument();
  });

  it("hides the AI method when AI is disabled for the organization", async () => {
    renderDialog(buildWorkspace({ aiEnabled: false }));

    expect(await screen.findByText("From code")).toBeInTheDocument();
    expect(screen.queryByText("Create with AI")).not.toBeInTheDocument();
  });

  it("disables the AI method once the AI budget is reached", async () => {
    renderDialog(buildWorkspace({ aiBudgetLimitReached: true }));

    const aiCard = (await screen.findByText("Create with AI")).closest(
      "button",
    );
    expect(aiCard).toBeDisabled();
    expect(screen.getByText("Monthly AI budget reached")).toBeInTheDocument();
  });

  it("hides the Superset method when the workspace has no Superset instance", async () => {
    renderDialog();

    expect(await screen.findByText("iFrame")).toBeInTheDocument();
    expect(screen.queryByText("Superset")).not.toBeInTheDocument();
  });

  it.each([
    ["From code", "STATIC"],
    ["iFrame", "IFRAME"],
  ])(
    "opens the create form with %s pre-selected",
    async (label, expectedType) => {
      const user = userEvent.setup();
      renderDialog();

      await user.click(await screen.findByText(label));

      expect(mockRouter).toMatchObject({
        pathname: "/workspaces/test-workspace/webapps/create",
        query: { type: expectedType },
      });
    },
  );

  it("shows the AI prompt when choosing to create with AI", async () => {
    const user = userEvent.setup();
    renderDialog();

    await user.click(await screen.findByText("Create with AI"));

    expect(screen.getByText("What do you want to build?")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Create" })).toBeDisabled();
  });
});
