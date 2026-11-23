import { InMemoryCache } from "@apollo/client";
import { act, renderHook, waitFor } from "@testing-library/react";
import { ReactNode } from "react";
import { toast } from "react-toastify";
import { CACHE_CONFIG } from "core/helpers/apollo";
import { TestApp } from "core/helpers/testutils";
import { WorkspaceCopyRunStatus } from "graphql/types";
import {
  ActiveWorkspaceCopyRunDocument,
  FinishedWorkspaceCopyRunDocument,
} from "workspaces/graphql/queries.generated";
import useActiveWorkspaceCopyRun from "./useActiveWorkspaceCopyRun";

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), warning: jest.fn(), error: jest.fn() },
}));

const run = (status: WorkspaceCopyRunStatus) => ({
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
  workspace: null,
});

const activeRunMock = (active: ReturnType<typeof run> | null) => ({
  request: { query: ActiveWorkspaceCopyRunDocument },
  result: { data: { activeWorkspaceCopyRun: active } },
});

const finishedRunMock = (status: WorkspaceCopyRunStatus) => ({
  request: {
    query: FinishedWorkspaceCopyRunDocument,
    variables: { id: "run-1" },
  },
  result: { data: { workspaceCopyRun: run(status) } },
});

const followCopyUntilItEnds = async (
  finalStatus: WorkspaceCopyRunStatus,
  onFinished = jest.fn(),
) => {
  const wrapper = ({ children }: { children: ReactNode }) => (
    <TestApp
      mocks={[
        activeRunMock(run(WorkspaceCopyRunStatus.Running)),
        activeRunMock(null),
        finishedRunMock(finalStatus),
      ]}
      cache={new InMemoryCache(CACHE_CONFIG)}
    >
      {children}
    </TestApp>
  );
  const { result } = renderHook(() => useActiveWorkspaceCopyRun(onFinished), {
    wrapper,
  });

  await waitFor(() => expect(result.current.run?.id).toBe("run-1"));
  expect(onFinished).not.toHaveBeenCalled();

  await act(async () => {
    await result.current.refetch();
  });
  await waitFor(() => expect(result.current.run).toBeNull());
  return onFinished;
};

describe("useActiveWorkspaceCopyRun", () => {
  beforeEach(() => jest.clearAllMocks());

  it("refreshes the page and announces a copy that succeeded", async () => {
    const onFinished = await followCopyUntilItEnds(
      WorkspaceCopyRunStatus.Success,
    );

    expect(onFinished).toHaveBeenCalledTimes(1);
    await waitFor(() =>
      expect(toast.success).toHaveBeenCalledWith("{{name}} is ready."),
    );
  });

  it("tells the user when the copy failed", async () => {
    await followCopyUntilItEnds(WorkspaceCopyRunStatus.Failed);

    await waitFor(() =>
      expect(toast.error).toHaveBeenCalledWith("The duplication failed."),
    );
    expect(toast.success).not.toHaveBeenCalled();
  });
});
