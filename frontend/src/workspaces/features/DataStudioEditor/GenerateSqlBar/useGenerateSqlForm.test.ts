import { act, renderHook } from "@testing-library/react";
import { GenerateSqlPhase, useGenerateSqlForm } from "./useGenerateSqlForm";

const mockCreateConversation = jest.fn();
const mockSend = jest.fn();
const mockAbort = jest.fn();
let mockStreamError: string | null = null;
let capturedHandlers: Record<string, (data: unknown) => void> = {};

jest.mock("assistant/graphql/mutations.generated", () => ({
  useCreateAssistantConversationMutation: () => [mockCreateConversation],
}));

jest.mock("core/hooks/useStreamingFetch", () => ({
  __esModule: true,
  default: (handlers: Record<string, (data: unknown) => void>) => {
    capturedHandlers = handlers;
    return { send: mockSend, abort: mockAbort, streamError: mockStreamError };
  },
}));

const onGenerated = jest.fn();

const resolveConversation = (id: string | null) =>
  mockCreateConversation.mockResolvedValue({
    data: { createAssistantConversation: { conversation: id ? { id } : null } },
  });

const submitPrompt = async (
  result: { current: ReturnType<typeof useGenerateSqlForm> },
  prompt: string,
) => {
  act(() => result.current.setPrompt(prompt));
  await act(async () => {
    await result.current.handleSubmit();
  });
};

beforeEach(() => {
  mockCreateConversation.mockReset();
  mockSend.mockReset();
  mockAbort.mockReset();
  onGenerated.mockReset();
  mockStreamError = null;
  capturedHandlers = {};
});

describe("useGenerateSqlForm", () => {
  it("does nothing on submit with an empty prompt", async () => {
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );
    await act(async () => {
      await result.current.handleSubmit();
    });
    expect(mockCreateConversation).not.toHaveBeenCalled();
  });

  it("creates a conversation for the generate_sql instruction set and sends the prompt", async () => {
    resolveConversation("conv-1");
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );

    await submitPrompt(result, "top 10 patients");

    expect(mockCreateConversation).toHaveBeenCalledWith({
      variables: {
        input: { workspaceSlug: "ws-1", instructionSet: "generate_sql" },
      },
    });
    expect(mockSend).toHaveBeenCalledWith(
      expect.stringContaining("/assistant/conversations/conv-1/stream/"),
      { message: "top 10 patients" },
    );
    expect(result.current.phase).toBe(GenerateSqlPhase.Generating);
  });

  it("moves to the Done phase, then calls onGenerated after a short pause", async () => {
    jest.useFakeTimers();
    resolveConversation("conv-1");
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );
    await submitPrompt(result, "top 10 patients");

    act(() =>
      capturedHandlers.done({ output: "SELECT * FROM patients LIMIT 10" }),
    );

    // The success checkmark is shown for a moment before the dialog closes,
    // mirroring useAIForm's pause before navigating away.
    expect(onGenerated).not.toHaveBeenCalled();
    expect(result.current.phase).toBe(GenerateSqlPhase.Done);

    act(() => jest.advanceTimersByTime(500));

    expect(onGenerated).toHaveBeenCalledWith("SELECT * FROM patients LIMIT 10");
    jest.useRealTimers();
  });

  it("moves to the error phase when done fires without output", async () => {
    resolveConversation("conv-1");
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );
    await submitPrompt(result, "top 10 patients");

    act(() => capturedHandlers.done({ output: null }));

    expect(onGenerated).not.toHaveBeenCalled();
    expect(result.current.phase).toBe(GenerateSqlPhase.Error);
    expect(result.current.error).toBeTruthy();
  });

  it("surfaces a mapped message when the error event fires", async () => {
    resolveConversation("conv-1");
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );
    await submitPrompt(result, "top 10 patients");

    act(() => capturedHandlers.error({ error_code: "MAX_TOKENS_REACHED" }));

    expect(result.current.phase).toBe(GenerateSqlPhase.Error);
    expect(result.current.error).toMatch(/token limit/i);
  });

  it("moves to the error phase when conversation creation returns no id", async () => {
    resolveConversation(null);
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );

    await submitPrompt(result, "top 10 patients");

    expect(mockSend).not.toHaveBeenCalled();
    expect(result.current.phase).toBe(GenerateSqlPhase.Error);
  });

  it("moves to the error phase when conversation creation throws", async () => {
    mockCreateConversation.mockRejectedValue(new Error("network down"));
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );

    await submitPrompt(result, "top 10 patients");

    expect(result.current.phase).toBe(GenerateSqlPhase.Error);
  });

  it("does not resubmit while already generating", async () => {
    resolveConversation("conv-1");
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );
    await submitPrompt(result, "top 10 patients");
    mockCreateConversation.mockClear();

    await act(async () => {
      await result.current.handleSubmit();
    });

    expect(mockCreateConversation).not.toHaveBeenCalled();
  });

  it("cancel aborts the stream and resets to idle", async () => {
    resolveConversation("conv-1");
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );
    await submitPrompt(result, "top 10 patients");

    act(() => result.current.cancel());

    expect(mockAbort).toHaveBeenCalled();
    expect(result.current.phase).toBe(GenerateSqlPhase.Idle);
  });

  it("reset clears the prompt and error", async () => {
    resolveConversation(null);
    const { result } = renderHook(() =>
      useGenerateSqlForm("ws-1", onGenerated),
    );
    await submitPrompt(result, "top 10 patients");
    expect(result.current.phase).toBe(GenerateSqlPhase.Error);

    act(() => result.current.reset());

    expect(result.current.prompt).toBe("");
    expect(result.current.error).toBeNull();
    expect(result.current.phase).toBe(GenerateSqlPhase.Idle);
  });
});
