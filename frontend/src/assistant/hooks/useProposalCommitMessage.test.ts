import { act, renderHook } from "@testing-library/react";
import useProposalCommitMessage from "./useProposalCommitMessage";

describe("useProposalCommitMessage", () => {
  it("takes the message the proposal came with", () => {
    const { result } = renderHook(() => useProposalCommitMessage());

    act(() => result.current.receiveCommitMessage("Add retry logic"));

    expect(result.current.commitMessage).toBe("Add retry logic");
  });

  it("keeps a user edit when the same proposal is re-emitted", () => {
    const { result } = renderHook(() => useProposalCommitMessage());

    act(() => result.current.receiveCommitMessage("Add retry logic"));
    act(() => result.current.setCommitMessage("Add retry logic and a cap"));
    act(() => result.current.receiveCommitMessage("Add retry logic"));

    expect(result.current.commitMessage).toBe("Add retry logic and a cap");
  });

  it("replaces a user edit when the agent proposes a new message", () => {
    const { result } = renderHook(() => useProposalCommitMessage());

    act(() => result.current.receiveCommitMessage("Add retry logic"));
    act(() => result.current.setCommitMessage("Add retry logic and a cap"));
    act(() => result.current.receiveCommitMessage("Lower the batch size"));

    expect(result.current.commitMessage).toBe("Lower the batch size");
  });

  it("takes the next message again after a reset", () => {
    const { result } = renderHook(() => useProposalCommitMessage());

    act(() => result.current.receiveCommitMessage("Add retry logic"));
    act(() => result.current.resetCommitMessage());
    expect(result.current.commitMessage).toBeNull();

    act(() => result.current.receiveCommitMessage("Add retry logic"));
    expect(result.current.commitMessage).toBe("Add retry logic");
  });
});
