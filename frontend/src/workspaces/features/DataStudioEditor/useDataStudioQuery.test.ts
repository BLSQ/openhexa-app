import { act, renderHook } from "@testing-library/react";
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

const withResult = (executeSQL: unknown) => ({
  loading: false,
  data: { workspace: { database: { executeSQL } } },
});

beforeEach(() => {
  mockExecute.mockClear();
  (downloadQueryCsv as jest.Mock).mockClear();
  (buildCsv as jest.Mock).mockClear();
  (downloadCsvBlob as jest.Mock).mockClear();
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

  it("builds the CSV client-side when the result is complete (not truncated)", () => {
    mockState = withResult({
      success: true,
      truncated: false,
      columns: ["id"],
      rows: [{ id: 1 }],
    });
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.run("SELECT 2", 50));

    act(() => result.current.downloadCsv());

    expect(buildCsv).toHaveBeenCalledWith(["id"], [{ id: 1 }]);
    expect(downloadCsvBlob).toHaveBeenCalledWith(
      "query-results.csv",
      "CSV_CONTENT",
    );
    expect(downloadQueryCsv).not.toHaveBeenCalled();
  });

  it("streams from the server the last run query when the result was truncated", () => {
    mockState = withResult({
      success: true,
      truncated: true,
      rows: [{ id: 1 }],
    });
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    // Runs a query (which may be a selection), then exports: the server export
    // must use what was run, not the editor contents.
    act(() => result.current.run("SELECT 2", 50));

    act(() => result.current.downloadCsv());

    expect(downloadQueryCsv).toHaveBeenCalledWith("ws-1", "SELECT 2");
    expect(downloadCsvBlob).not.toHaveBeenCalled();
  });

  it("does not download before any query has run", () => {
    const { result } = renderHook(() => useDataStudioQuery("ws-1"));
    act(() => result.current.downloadCsv());
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
