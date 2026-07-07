import { act, renderHook } from "@testing-library/react";
import { useDataStudioQuery } from "./useDataStudioQuery";

const mockExecute = jest.fn();
let mockState: { data?: unknown; loading: boolean; error?: unknown };

jest.mock("./DataStudioEditor.generated", () => ({
  useExecuteWorkspaceSqlLazyQuery: () => [mockExecute, mockState],
}));

const withResult = (executeSQL: unknown) => ({
  loading: false,
  data: { workspace: { database: { executeSQL } } },
});

beforeEach(() => {
  mockExecute.mockClear();
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
