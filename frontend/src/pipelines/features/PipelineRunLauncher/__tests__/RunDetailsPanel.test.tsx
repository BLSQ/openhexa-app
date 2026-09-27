import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PipelineRunStatus, PipelineRunTrigger } from "graphql/types";
import usePipelineRunDetail from "pipelines/features/PipelineRunDetail/usePipelineRunDetail";
import RunDetailsPanel from "../RunDetailsPanel";

jest.mock("pipelines/features/PipelineRunDetail/usePipelineRunDetail", () => ({
  __esModule: true,
  default: jest.fn(),
}));
jest.mock("pipelines/features/RunMessages", () => ({
  __esModule: true,
  default: () => <div>messages</div>,
}));
jest.mock("pipelines/features/RunLogs", () => ({
  __esModule: true,
  default: () => <div>logs</div>,
}));
jest.mock("workspaces/features/RunOutputsTable", () => ({
  __esModule: true,
  default: () => <div>outputs</div>,
}));
jest.mock("workspaces/features/StopPipelineDialog", () => ({
  __esModule: true,
  default: ({ open }: { open: boolean }) =>
    open ? <div>stop-dialog</div> : null,
}));
jest.mock("core/features/User", () => ({
  __esModule: true,
  default: () => <span>user</span>,
}));

const detailMock = usePipelineRunDetail as jest.Mock;

const mockRun = (status: PipelineRunStatus, isFinished: boolean) => {
  detailMock.mockReturnValue({
    data: { workspace: { slug: "ws" } },
    isFinished,
    run: {
      id: "run-1",
      status,
      executionDate: new Date().toISOString(),
      duration: isFinished ? 42 : null,
      triggerMode: PipelineRunTrigger.Manual,
      version: { versionName: "v12" },
      user: null,
      logs: "",
      datasetVersions: [],
      outputs: [],
      hasErrorMessages: false,
      pipeline: { code: "weekly", permissions: { stopPipeline: true } },
    },
    messageStream: {
      messages: [],
      isStreaming: false,
      streamError: null,
      reload: jest.fn(),
    },
  });
};

const renderPanel = (onRunAgain = jest.fn().mockResolvedValue(undefined)) =>
  render(
    <RunDetailsPanel
      workspaceSlug="ws"
      pipelineCode="weekly"
      pipelineName="weekly-cases"
      runId="run-1"
      canRun
      onClose={jest.fn()}
      onRunAgain={onRunAgain}
    />,
  );

describe("RunDetailsPanel", () => {
  it("offers Stop while the run is active", async () => {
    mockRun(PipelineRunStatus.Running, false);
    renderPanel();
    expect(screen.queryByText("Run again")).not.toBeInTheDocument();
    expect(screen.queryByText("outputs")).not.toBeInTheDocument();
    await userEvent.click(screen.getByText("Stop"));
    expect(screen.getByText("stop-dialog")).toBeInTheDocument();
  });

  it("offers Run again once the run is finished", async () => {
    mockRun(PipelineRunStatus.Success, true);
    const onRunAgain = jest.fn().mockResolvedValue(undefined);
    renderPanel(onRunAgain);
    expect(screen.queryByText("Stop")).not.toBeInTheDocument();
    expect(screen.getByText("No outputs")).toBeInTheDocument();
    expect(screen.getByText("0:42")).toBeInTheDocument();
    await userEvent.click(screen.getByText("Run again"));
    expect(onRunAgain).toHaveBeenCalled();
  });

  it("links to the full run page", () => {
    mockRun(PipelineRunStatus.Running, false);
    renderPanel();
    expect(screen.getByText("Open full run page").closest("a")).toHaveAttribute(
      "href",
      "/workspaces/ws/pipelines/weekly/runs/run-1",
    );
  });
});
