import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import {
  DuplicateWorkspaceError,
  WorkspaceCopyResource,
  WorkspaceCopyRunStatus,
} from "graphql/types";
import { DuplicateWorkspaceDocument } from "workspaces/graphql/mutations.generated";
import { WorkspaceCopyRunDocument } from "workspaces/graphql/queries.generated";
import DuplicateWorkspaceDialog from "./DuplicateWorkspaceDialog";

// The real picker fetches every country; the dialog only needs to pass its value through.
jest.mock("core/features/CountryPicker", () => {
  const CountryPicker = () => <div data-testid="country-picker" />;
  CountryPicker.fragments = {
    country: jest.requireActual("@apollo/client")
      .gql`fragment CountryPicker_country on Country { code alpha3 name }`,
  };
  return { __esModule: true, default: CountryPicker };
});

const WORKSPACE = {
  slug: "malaria",
  name: "Malaria",
  countries: [{ code: "BE", alpha3: "BEL", name: "Belgium" }],
  permissions: { duplicate: true },
};

const ALL_RESOURCES = Object.values(WorkspaceCopyResource);

const duplicateMock = (
  input: Record<string, any>,
  result: Record<string, any>,
) => ({
  request: {
    query: DuplicateWorkspaceDocument,
    variables: {
      input: {
        workspaceSlug: "malaria",
        name: "Malaria (copy)",
        countries: [{ code: "BE" }],
        resources: ALL_RESOURCES,
        includeConnectionSecrets: true,
        ...input,
      },
    },
  },
  result: {
    data: {
      duplicateWorkspace: {
        __typename: "DuplicateWorkspaceResult",
        success: true,
        errors: [],
        run: null,
        ...result,
      },
    },
  },
});

const runMock = (status: WorkspaceCopyRunStatus, logs: string) => ({
  request: { query: WorkspaceCopyRunDocument, variables: { id: "run-1" } },
  result: {
    data: {
      workspaceCopyRun: {
        __typename: "WorkspaceCopyRun",
        id: "run-1",
        status,
        logs,
        error: null,
        workspace:
          status === WorkspaceCopyRunStatus.Success
            ? { __typename: "Workspace", slug: "copy-of-malaria-ab12" }
            : null,
      },
    },
  },
});

const RUN = {
  __typename: "WorkspaceCopyRun",
  id: "run-1",
  status: WorkspaceCopyRunStatus.Queued,
};

const renderDialog = (mocks: any[]) =>
  render(
    <TestApp mocks={mocks}>
      <DuplicateWorkspaceDialog
        open={true}
        workspace={WORKSPACE}
        onClose={jest.fn()}
      />
    </TestApp>,
  );

// The test `t` does not interpolate, so the prefilled "Copy of {{name}}" is replaced.
const typeName = async (user: ReturnType<typeof userEvent.setup>) => {
  const input = screen.getByLabelText("New workspace name");
  await user.clear(input);
  await user.type(input, "Malaria (copy)");
};

describe("DuplicateWorkspaceDialog", () => {
  it("duplicates every resource by default, then follows the run", async () => {
    const user = userEvent.setup();
    renderDialog([
      duplicateMock({}, { run: RUN }),
      runMock(
        WorkspaceCopyRunStatus.Success,
        "10:00:00 => Copying files ...\n10:00:01 [WARNING] skipped one\n",
      ),
    ]);

    expect(screen.getByLabelText("New workspace name")).toHaveValue(
      "Copy of {{name}}",
    );
    for (const label of ["Files", "Workspace database", "Web apps"]) {
      expect(screen.getByLabelText(label)).toBeChecked();
    }

    await typeName(user);
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(
      await screen.findByRole("button", { name: "Open workspace" }),
    ).toBeInTheDocument();
    expect(screen.getByText("10:00:01 [WARNING] skipped one")).toHaveClass(
      "text-amber-300",
    );
  });

  it("does not copy secrets when connections are left out", async () => {
    const user = userEvent.setup();
    renderDialog([
      duplicateMock(
        {
          resources: ALL_RESOURCES.filter(
            (r) => r !== WorkspaceCopyResource.Connections,
          ),
          includeConnectionSecrets: false,
        },
        { run: RUN },
      ),
      runMock(
        WorkspaceCopyRunStatus.Running,
        "10:00:00 => Copying files ...\n",
      ),
    ]);

    await typeName(user);
    await user.click(screen.getByLabelText("Connections"));
    expect(
      screen.queryByLabelText("Include connection secrets"),
    ).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(
      await screen.findByText("10:00:00 => Copying files ..."),
    ).toBeVisible();
    expect(
      screen.queryByRole("button", { name: "Open workspace" }),
    ).not.toBeInTheDocument();
  });

  it("shows why a duplication is refused", async () => {
    const user = userEvent.setup();
    renderDialog([
      duplicateMock(
        {},
        {
          success: false,
          errors: [DuplicateWorkspaceError.WorkspacesLimitReached],
        },
      ),
    ]);

    await typeName(user);
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(
      await screen.findByText(
        "You have reached the maximum number of workspaces for your plan.",
      ),
    ).toBeVisible();
  });
});
