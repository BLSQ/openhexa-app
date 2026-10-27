import { act, renderHook, waitFor } from "@testing-library/react";
import { TextDecoder, TextEncoder } from "util";
import useStreamingFetch from "../useStreamingFetch";

// jsdom does not expose the encoding API the hook relies on.
Object.assign(global, { TextEncoder, TextDecoder });

// jsdom has no global Response, so build the minimal shape the hook reads.
function fakeResponse(
  status: number,
  contentType: string,
  text: string,
): Response {
  let consumed = false;
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: { get: () => contentType },
    json: () => Promise.resolve(JSON.parse(text)),
    body: {
      getReader: () => ({
        read: () => {
          if (consumed)
            return Promise.resolve({ done: true, value: undefined });
          consumed = true;
          return Promise.resolve({
            done: false,
            value: new TextEncoder().encode(text),
          });
        },
      }),
    },
  } as unknown as Response;
}

function jsonResponse(status: number, body: unknown): Response {
  return fakeResponse(status, "application/json", JSON.stringify(body));
}

function sseResponse(events: string): Response {
  return fakeResponse(200, "text/event-stream", events);
}

describe("useStreamingFetch", () => {
  const onError = jest.fn();
  const onDone = jest.fn();

  beforeEach(() => {
    onError.mockReset();
    onDone.mockReset();
    global.fetch = jest.fn();
  });

  it("dispatches a server error_code to the error handler", async () => {
    (global.fetch as jest.Mock).mockResolvedValue(
      jsonResponse(403, { error: "Budget", error_code: "AI_BUDGET_EXCEEDED" }),
    );
    const { result } = renderHook(() =>
      useStreamingFetch({ error: onError, done: onDone }),
    );

    await act(() => result.current.send("/stream", { message: "hi" }));

    expect(onError).toHaveBeenCalledWith({ error_code: "AI_BUDGET_EXCEEDED" });
    expect(result.current.streamError).toBeNull();
    expect(result.current.isStreaming).toBe(false);
  });

  it("reports a connection failure for a non-OK response without error_code", async () => {
    (global.fetch as jest.Mock).mockResolvedValue(
      fakeResponse(500, "text/html", "boom"),
    );
    const { result } = renderHook(() =>
      useStreamingFetch({ error: onError, done: onDone }),
    );

    await act(() => result.current.send("/stream", { message: "hi" }));

    await waitFor(() =>
      expect(result.current.streamError).toBe("connection_failed"),
    );
    expect(onError).not.toHaveBeenCalled();
  });

  it("parses SSE events from a successful stream", async () => {
    (global.fetch as jest.Mock).mockResolvedValue(
      sseResponse('event: done\ndata: {"name":"Chat"}\n\n'),
    );
    const { result } = renderHook(() =>
      useStreamingFetch({ error: onError, done: onDone }),
    );

    await act(() => result.current.send("/stream", { message: "hi" }));

    expect(onDone).toHaveBeenCalledWith({ name: "Chat" });
    expect(onError).not.toHaveBeenCalled();
    expect(result.current.streamError).toBeNull();
  });
});
