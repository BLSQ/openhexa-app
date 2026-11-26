import { InMemoryCache } from "@apollo/client";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CACHE_CONFIG } from "core/helpers/apollo";
import { TestApp } from "core/helpers/testutils";
import {
  DuplicateWorkspaceError,
  WorkspaceCopyResource,
  WorkspaceCopyRunStatus,
  WorkspaceCopyStepName,
  WorkspaceCopyStepStatus,
} from "graphql/types";
import { DuplicateWorkspaceDocument } from "workspaces/graphql/mutations.generated";
import {
  ActiveWorkspaceCopyRunDocument,
  WorkspaceCopyRunDocument,
  WorkspaceDatabaseInUseDocument,
} from "workspaces/graphql/queries.generated";
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

const step = (
  name: WorkspaceCopyStepName,
  status: WorkspaceCopyStepStatus,
) => ({
  __typename: "WorkspaceCopyStep",
  name,
  status,
});

const run = (
  status: WorkspaceCopyRunStatus,
  slug: string | null = null,
  {
    steps = [
      step(WorkspaceCopyStepName.Workspace, WorkspaceCopyStepStatus.Pending),
    ],
    warnings = [] as string[],
  } = {},
) => ({
  __typename: "WorkspaceCopyRun",
  id: "run-1",
  status,
  targetWorkspaceName: "Malaria (copy)",
  sourceWorkspaceSlug: "malaria",
  sourceWorkspace: {
    __typename: "Workspace",
    slug: "malaria",
    name: "Malaria",
  },
  error: null,
  steps,
  warnings,
  workspace: slug
    ? { __typename: "Workspace", slug, name: "Malaria (copy)" }
    : null,
});

const activeRunMock = (active: ReturnType<typeof run> | null) => ({
  request: { query: ActiveWorkspaceCopyRunDocument },
  result: { data: { activeWorkspaceCopyRun: active } },
});

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
        includeConnectionSecrets: false,
        allDatasetVersions: false,
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

const databaseInUseMock = (slug: string, databaseInUse: boolean) => ({
  request: {
    query: WorkspaceDatabaseInUseDocument,
    variables: { slug },
  },
  result: {
    data: {
      workspace: { __typename: "Workspace", slug, databaseInUse },
    },
  },
});

const pollMock = (
  status: WorkspaceCopyRunStatus,
  text: string,
  slug: string | null = null,
  extra: Parameters<typeof run>[2] = {},
) => ({
  request: {
    query: WorkspaceCopyRunDocument,
    variables: { id: "run-1", logsOffset: 0 },
  },
  result: {
    data: {
      workspaceCopyRun: {
        ...run(status, slug, extra),
        logs: {
          __typename: "WorkspaceCopyRunLogs",
          text,
          nextOffset: text.length,
        },
      },
    },
  },
});

const renderDialog = (
  mocks: any[],
  workspace: typeof WORKSPACE | null = WORKSPACE,
  { databaseInUse = false } = {},
) =>
  render(
    <TestApp
      mocks={
        workspace
          ? [databaseInUseMock(workspace.slug, databaseInUse), ...mocks]
          : mocks
      }
      cache={new InMemoryCache(CACHE_CONFIG)}
    >
      <DuplicateWorkspaceDialog
        open={true}
        workspace={workspace}
        onClose={jest.fn()}
      />
    </TestApp>,
  );

// The test `t` does not interpolate, so the prefilled "Copy of {{name}}" is replaced.
const typeName = async (user: ReturnType<typeof userEvent.setup>) => {
  const input = await screen.findByLabelText("New workspace name");
  await user.clear(input);
  await user.type(input, "Malaria (copy)");
};

describe("DuplicateWorkspaceDialog", () => {
  it("duplicates every resource by default, then follows the run", async () => {
    const user = userEvent.setup();
    renderDialog([
      activeRunMock(null),
      duplicateMock({}, { run: run(WorkspaceCopyRunStatus.Queued) }),
      pollMock(
        WorkspaceCopyRunStatus.Success,
        "10:00:00 => Copying files ...\n10:00:01 [WARNING] skipped one\n",
        "malaria-copy",
        {
          steps: [
            step(
              WorkspaceCopyStepName.Workspace,
              WorkspaceCopyStepStatus.Success,
            ),
            step(
              WorkspaceCopyStepName.Pipelines,
              WorkspaceCopyStepStatus.SuccessWithWarnings,
            ),
          ],
          warnings: ["pipeline 'etl' schedule not copied"],
        },
      ),
    ]);

    expect(await screen.findByLabelText("New workspace name")).toHaveValue(
      "Copy of {{name}}",
    );
    for (const label of ["Files", "Workspace database", "Web apps"]) {
      expect(screen.getByLabelText(label)).toBeChecked();
    }
    expect(
      screen.getByLabelText("Include connection secrets"),
    ).not.toBeChecked();
    expect(
      screen.getByLabelText("Copy all dataset versions"),
    ).not.toBeChecked();

    await typeName(user);
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(
      await screen.findByRole("button", { name: "Open {{name}}" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Done, with warnings")).toBeVisible();
    expect(
      screen.getByText("pipeline 'etl' schedule not copied"),
    ).toBeVisible();
    expect(
      screen.getByText(
        "Pipeline schedules are not copied: set them again in the new workspace once you have checked the pipelines.",
      ),
    ).toBeVisible();
    expect(
      screen.getByText("10:00:01 [WARNING] skipped one"),
    ).not.toBeVisible();
    await user.click(screen.getByText("Show details"));
    expect(screen.getByText("10:00:01 [WARNING] skipped one")).toHaveClass(
      "text-amber-300",
    );
  });

  it("does not copy secrets when connections are left out", async () => {
    const user = userEvent.setup();
    renderDialog([
      activeRunMock(null),
      duplicateMock(
        {
          resources: ALL_RESOURCES.filter(
            (r) => r !== WorkspaceCopyResource.Connections,
          ),
          includeConnectionSecrets: false,
        },
        { run: run(WorkspaceCopyRunStatus.Queued) },
      ),
      pollMock(WorkspaceCopyRunStatus.Queued, ""),
    ]);

    await typeName(user);
    await user.click(screen.getByLabelText("Connections"));
    expect(
      screen.queryByLabelText("Include connection secrets"),
    ).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(await screen.findByText("Waiting")).toBeVisible();
    expect(
      screen.queryByRole("button", { name: "Open {{name}}" }),
    ).not.toBeInTheDocument();
  });

  it("shows a copy still running when opened again", async () => {
    const steps = [
      step(WorkspaceCopyStepName.Workspace, WorkspaceCopyStepStatus.Success),
      step(WorkspaceCopyStepName.Files, WorkspaceCopyStepStatus.Running),
    ];
    renderDialog([
      activeRunMock(run(WorkspaceCopyRunStatus.Running, null, { steps })),
      pollMock(
        WorkspaceCopyRunStatus.Running,
        "10:00:00 => Copying files ...\n",
        null,
        { steps },
      ),
    ]);

    expect(await screen.findByText("Copying…")).toBeVisible();
    expect(screen.getByText("Done")).toBeVisible();
    expect(
      await screen.findByText("10:00:00 => Copying files ..."),
    ).toBeInTheDocument();
    expect(
      screen.queryByLabelText("New workspace name"),
    ).not.toBeInTheDocument();
  });

  it("switches to the copy already running instead of starting another", async () => {
    const user = userEvent.setup();
    renderDialog([
      activeRunMock(null),
      duplicateMock(
        {},
        {
          success: false,
          errors: [DuplicateWorkspaceError.CopyAlreadyRunning],
        },
      ),
      activeRunMock(run(WorkspaceCopyRunStatus.Running)),
      pollMock(
        WorkspaceCopyRunStatus.Running,
        "10:00:00 => Copying files ...\n",
      ),
    ]);

    await typeName(user);
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(
      await screen.findByText("10:00:00 => Copying files ..."),
    ).toBeInTheDocument();
  });

  it("sends the dataset versions option when datasets are copied", async () => {
    const user = userEvent.setup();
    renderDialog([
      activeRunMock(null),
      duplicateMock(
        { allDatasetVersions: true, includeConnectionSecrets: true },
        { run: run(WorkspaceCopyRunStatus.Queued) },
      ),
      pollMock(WorkspaceCopyRunStatus.Queued, ""),
    ]);

    await typeName(user);
    await user.click(screen.getByLabelText("Copy all dataset versions"));
    await user.click(screen.getByLabelText("Include connection secrets"));
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(await screen.findByText("Waiting")).toBeVisible();
  });

  it("leaves the database out while it is in use", async () => {
    const user = userEvent.setup();
    renderDialog(
      [
        activeRunMock(null),
        duplicateMock(
          {
            resources: ALL_RESOURCES.filter(
              (r) => r !== WorkspaceCopyResource.Database,
            ),
          },
          { run: run(WorkspaceCopyRunStatus.Queued) },
        ),
        pollMock(WorkspaceCopyRunStatus.Queued, ""),
      ],
      WORKSPACE,
      { databaseInUse: true },
    );

    await typeName(user);
    const database = await screen.findByLabelText("Workspace database");
    await screen.findByText(
      "The database is in use and cannot be copied. Close the notebooks, pipelines and tools connected to it, then reopen this dialog.",
    );
    expect(database).not.toBeChecked();
    expect(database).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(await screen.findByText("Waiting")).toBeVisible();
  });

  it("shows why a duplication is refused", async () => {
    const user = userEvent.setup();
    renderDialog([
      activeRunMock(null),
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

  it("explains that a country was refused", async () => {
    const user = userEvent.setup();
    renderDialog([
      activeRunMock(null),
      duplicateMock(
        {},
        { success: false, errors: [DuplicateWorkspaceError.InvalidCountry] },
      ),
    ]);

    await typeName(user);
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(
      await screen.findByText(
        "One of the selected countries is not recognized.",
      ),
    ).toBeVisible();
  });

  it("shows an error instead of failing silently when the request fails", async () => {
    const user = userEvent.setup();
    renderDialog([
      activeRunMock(null),
      {
        ...duplicateMock({}, {}),
        result: undefined,
        error: new Error("Network error"),
      },
    ]);

    await typeName(user);
    await user.click(screen.getByRole("button", { name: "Duplicate" }));

    expect(
      await screen.findByText("An unexpected error occurred."),
    ).toBeVisible();
    expect(screen.getByRole("button", { name: "Duplicate" })).toBeEnabled();
  });

  it("explains that another workspace's copy is still running", async () => {
    renderDialog(
      [
        activeRunMock(run(WorkspaceCopyRunStatus.Running)),
        pollMock(WorkspaceCopyRunStatus.Running, ""),
      ],
      { ...WORKSPACE, slug: "cholera", name: "Cholera" },
    );

    expect(await screen.findByText("Copy in progress")).toBeVisible();
    expect(
      screen.getByText(
        "You can run one copy at a time. You can duplicate {{name}} once this one is done.",
      ),
    ).toBeVisible();
  });

  it("says when the copy it was opened for has already ended", async () => {
    renderDialog([activeRunMock(null)], null);

    expect(
      await screen.findByText("No copy is running anymore."),
    ).toBeVisible();
    expect(
      screen.queryByLabelText("New workspace name"),
    ).not.toBeInTheDocument();
  });
});
