import { act, renderHook } from "@testing-library/react";
import { toast } from "react-toastify";
import { buildCsv, downloadCsvBlob } from "./csv";
import { downloadQueryCsv } from "./downloadQueryCsv";
import { useDataStudioQuery } from "./useDataStudioQuery";

const mockExecute = jest.fn();
let mockState: { data?: unknown; loading: boolean; error?: unknown };

jest.mock("./DataStudioEditor.generated", () => ({
  useExecuteWorkspaceSqlLazyQuery: () => [mockExecute, mockState],
}));

jest.mock("./downloadQueryCsv", () => ({
  downloadQueryCsv: jest.fn(),
}));

jest.mock("./csv", () => ({
  buildCsv: jest.fn(() => "CSV_CONTENT"),
  downloadCsvBlob: jest.fn(),
}));

jest.mock("react-toastify", () => ({
  toast: { error: jest.fn(), info: jest.fn() },
}));

const withResult = (executeSQL: unknown) => ({
  loading: false,
  data: { workspace: { database: { executeSQL } } },
});

beforeEach(() => {
  mockExecute.mockClear();
  (downloadQueryCsv as jest.Mock).mockClear();
  (downloadQueryCsv as jest.Mock).mockResolvedValue(undefined);
  (buildCsv as jest.Mock).mockClear();
  (downloadCsvBlob as jest.Mock).mockClear();
  (toast.error as jest.Mock).mockClear();
  (toast.info as jest.Mock).mockClear();
  mockState = { loading: false };
});

describe("useDataStudioQuery", () => {
  it("runs a trimmed query with the workspace slug and max rows", () => {
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.run("  SELECT 1  ", 100));

    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 1", maxRows: 100 },
    });
  });

  it("ignores whitespace-only queries", () => {
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.run("   ", 50));
    expect(mockExecute).not.toHaveBeenCalled();
  });

  it("does not run while a query is already loading", () => {
    mockState = { loading: true };
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.run("SELECT 1", 50));
    expect(mockExecute).not.toHaveBeenCalled();
  });

  it("retries the exact variables of the last run", () => {
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.run("SELECT 1", 500));
    mockExecute.mockClear();

    act(() => result.current.retry());
    expect(mockExecute).toHaveBeenCalledWith({
      variables: { workspaceSlug: "ws-1", query: "SELECT 1", maxRows: 500 },
    });
  });

  it("does not retry before any query has run", () => {
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.retry());
    expect(mockExecute).not.toHaveBeenCalled();
  });

  it("builds the CSV client-side when the result is complete (not truncated)", async () => {
    mockState = withResult({
      success: true,
      truncated: false,
      columns: ["id"],
      rows: [{ id: 1 }],
    });
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.run("SELECT 2", 50));

    await act(async () => {
      await result.current.downloadCsv();
    });

    expect(buildCsv).toHaveBeenCalledWith(["id"], [{ id: 1 }]);
    expect(downloadCsvBlob).toHaveBeenCalledWith(
      "query-results.csv",
      "CSV_CONTENT",
    );
    expect(downloadQueryCsv).not.toHaveBeenCalled();
    // The fast client path is instant, so it must not warn about a wait.
    expect(toast.info).not.toHaveBeenCalled();
  });

  it("streams from the server the last run query when the result was truncated", async () => {
    mockState = withResult({
      success: true,
      truncated: true,
      rows: [{ id: 1 }],
    });
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    // Runs a query (which may be a selection), then exports: the server export
    // must use what was run, not the editor contents.
    act(() => result.current.run("SELECT 2", 50));

    await act(async () => {
      await result.current.downloadCsv();
    });

    expect(downloadQueryCsv).toHaveBeenCalledWith("ws-1", "SELECT 2");
    expect(downloadCsvBlob).not.toHaveBeenCalled();
    expect(result.current.exporting).toBe(false);
    // The heavy path re-runs server-side and can be slow, so it warns up front.
    expect(toast.info).toHaveBeenCalledTimes(1);
  });

  it("toasts and clears the exporting state when a server export fails", async () => {
    (downloadQueryCsv as jest.Mock).mockRejectedValue(new Error("boom"));
    mockState = withResult({
      success: true,
      truncated: true,
      rows: [{ id: 1 }],
    });
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.run("SELECT 2", 50));

    await act(async () => {
      await result.current.downloadCsv();
    });

    expect(toast.error).toHaveBeenCalledTimes(1);
    expect(result.current.exporting).toBe(false);
  });

  it("marks exporting while a server export is in flight", async () => {
    let resolveDownload!: () => void;
    (downloadQueryCsv as jest.Mock).mockReturnValue(
      new Promise<void>((res) => {
        resolveDownload = res;
      }),
    );
    mockState = withResult({
      success: true,
      truncated: true,
      rows: [{ id: 1 }],
    });
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.run("SELECT 2", 50));

    let call!: Promise<void>;
    act(() => {
      call = result.current.downloadCsv();
    });
    expect(result.current.exporting).toBe(true);

    await act(async () => {
      resolveDownload();
      await call;
    });
    expect(result.current.exporting).toBe(false);
  });

  it("does not download before any query has run", async () => {
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    await act(async () => {
      await result.current.downloadCsv();
    });
    expect(downloadQueryCsv).not.toHaveBeenCalled();
    expect(downloadCsvBlob).not.toHaveBeenCalled();
  });

  it("allows export for a successful result with rows", () => {
    mockState = withResult({ success: true, rows: [{ id: 1 }] });
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    expect(result.current.canExport).toBe(true);
    expect(result.current.result).toEqual({ success: true, rows: [{ id: 1 }] });
  });

  it("does not allow export for a successful result with no rows", () => {
    mockState = withResult({ success: true, rows: [] });
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    expect(result.current.canExport).toBe(false);
  });

  it("does not allow export for a failed result", () => {
    mockState = withResult({ success: false, rows: [] });
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    expect(result.current.canExport).toBe(false);
  });
});
