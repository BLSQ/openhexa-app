import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PipelineRunStatus } from "graphql/types";
import { usePipelineRunLauncherRunQuery } from "pipelines/graphql/queries.generated";
import RunStatusOverlay, { FINISHED_RUN_TTL_MS } from "../RunStatusOverlay";

jest.mock("pipelines/graphql/queries.generated", () => ({
  __esModule: true,
  usePipelineRunLauncherRunQuery: jest.fn(),
}));

jest.mock("pipelines/hooks/usePipelineRunPoller", () => ({
  __esModule: true,
  default: jest.fn(),
}));

const queryMock = usePipelineRunLauncherRunQuery as jest.Mock;

let statuses: Record<string, PipelineRunStatus>;

const makeRun = (id: string) => ({
  __typename: "PipelineRun",
  id,
  status: statuses[id],
  executionDate: new Date().toISOString(),
  duration: null,
  hasErrorMessages: false,
  version: { id: "v12", versionName: "v12" },
});

// Memoized per id/status so the watcher's effect only fires on real changes.
const runCache: Record<string, ReturnType<typeof makeRun>> = {};
const getRun = (id: string) => {
  const key = `${id}:${statuses[id]}`;
  runCache[key] ??= makeRun(id);
  return runCache[key];
};

const tracked = (id: string, startedAt: number) => ({
  id,
  startedAt,
  launchInput: {},
});

const renderOverlay = (
  props: Partial<React.ComponentProps<typeof RunStatusOverlay>> = {},
) => {
  const defaults = {
    pipelineName: "weekly-cases",
    trackedRuns: [tracked("run-1", 1)],
    hidden: false,
    onOpenDetails: jest.fn(),
    onDismiss: jest.fn(),
  };
  const merged = { ...defaults, ...props };
  const utils = render(<RunStatusOverlay {...merged} />);
  return { ...utils, props: merged };
};

describe("RunStatusOverlay", () => {
  beforeEach(() => {
    statuses = { "run-1": PipelineRunStatus.Running };
    queryMock.mockImplementation(({ variables }) => ({
      data: { run: getRun(variables.runId) },
    }));
  });

  it("shows the active run and opens its details", async () => {
    const { props } = renderOverlay();
    expect(screen.getByTestId("run-status-overlay")).toBeInTheDocument();
    expect(screen.getByText("weekly-cases")).toBeInTheDocument();
    await userEvent.click(screen.getByText("View details"));
    expect(props.onOpenDetails).toHaveBeenCalledWith("run-1");
  });

  it("is hidden while a panel is open", () => {
    renderOverlay({ hidden: true });
    expect(screen.queryByTestId("run-status-overlay")).not.toBeInTheDocument();
  });

  it("calls onDismiss from the close button", async () => {
    const { props } = renderOverlay();
    await userEvent.click(screen.getByTitle("Hide until next run"));
    expect(props.onDismiss).toHaveBeenCalled();
  });

  it("lists other runs behind an expandable section", async () => {
    statuses["run-2"] = PipelineRunStatus.Queued;
    const { props } = renderOverlay({
      trackedRuns: [tracked("run-1", 1), tracked("run-2", 2)],
    });
    expect(screen.getByText("{{count}} runs in progress")).toBeInTheDocument();
    await userEvent.click(screen.getByText("{{count}} other runs"));
    await userEvent.click(screen.getByText("Details"));
    // run-2 started last so it is primary; run-1 is in the list.
    expect(props.onOpenDetails).toHaveBeenCalledWith("run-1");
  });

  it("drops a finished run after the grace period", () => {
    jest.useFakeTimers();
    try {
      const { rerender, props } = renderOverlay();
      statuses["run-1"] = PipelineRunStatus.Success;
      rerender(<RunStatusOverlay {...props} />);
      expect(screen.getByTestId("run-status-overlay")).toBeInTheDocument();

      act(() => {
        jest.advanceTimersByTime(FINISHED_RUN_TTL_MS + 1000);
      });
      expect(
        screen.queryByTestId("run-status-overlay"),
      ).not.toBeInTheDocument();
    } finally {
      jest.useRealTimers();
    }
  });
});
