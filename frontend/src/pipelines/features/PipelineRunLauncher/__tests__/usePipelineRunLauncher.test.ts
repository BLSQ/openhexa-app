import { act, renderHook } from "@testing-library/react";
import { PipelineType } from "graphql/types";
import { runPipeline } from "workspaces/helpers/pipelines";
import usePipelineRunLauncher from "../usePipelineRunLauncher";

jest.mock("core/hooks/useCacheKey", () => ({
  __esModule: true,
  default: () => jest.fn(),
}));

jest.mock("workspaces/helpers/pipelines", () => ({
  ...jest.requireActual("workspaces/helpers/pipelines"),
  __esModule: true,
  runPipeline: jest.fn(),
}));

const runPipelineMock = runPipeline as jest.Mock;

const zipPipeline = { id: "p1", code: "weekly", type: PipelineType.ZipFile };
const notebookPipeline = {
  id: "p2",
  code: "notebook",
  type: PipelineType.Notebook,
};

describe("usePipelineRunLauncher", () => {
  beforeEach(() => {
    runPipelineMock.mockReset();
  });

  it("opens the form for zip pipelines without launching", () => {
    const { result } = renderHook(() => usePipelineRunLauncher(zipPipeline));
    act(() => {
      result.current.openRun();
    });
    expect(result.current.panel).toEqual({ view: "form" });
    expect(runPipelineMock).not.toHaveBeenCalled();
  });

  it("launches notebook pipelines directly and shows the run", async () => {
    runPipelineMock.mockResolvedValue({ id: "run-1" });
    const { result } = renderHook(() =>
      usePipelineRunLauncher(notebookPipeline),
    );
    await act(async () => {
      await result.current.openRun();
    });
    expect(runPipelineMock).toHaveBeenCalledWith(
      "p2",
      undefined,
      undefined,
      undefined,
      undefined,
    );
    expect(result.current.panel).toEqual({ view: "run", runId: "run-1" });
    expect(result.current.trackedRuns.map((r) => r.id)).toEqual(["run-1"]);
  });

  it("tracks launched runs and reruns with the same input", async () => {
    runPipelineMock
      .mockResolvedValueOnce({ id: "run-1" })
      .mockResolvedValueOnce({ id: "run-2" });
    const { result } = renderHook(() => usePipelineRunLauncher(zipPipeline));
    const input = {
      config: { week: "2026-W27" },
      versionId: "v12",
      sendMailNotifications: false,
      enableDebugLogs: true,
    };

    await act(async () => {
      await result.current.launch(input);
    });
    act(() => {
      result.current.dismissOverlay();
    });
    expect(result.current.overlayDismissed).toBe(true);

    await act(async () => {
      await result.current.rerun("run-1");
    });
    expect(runPipelineMock).toHaveBeenLastCalledWith(
      "p1",
      { week: "2026-W27" },
      "v12",
      false,
      true,
    );
    expect(result.current.trackedRuns.map((r) => r.id)).toEqual([
      "run-1",
      "run-2",
    ]);
    expect(result.current.panel).toEqual({ view: "run", runId: "run-2" });
    expect(result.current.overlayDismissed).toBe(false);
  });
});
