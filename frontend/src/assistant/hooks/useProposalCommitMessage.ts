import { useCallback, useRef, useState } from "react";

/**
 * The commit message of the pending proposal, editable while the user reviews it.
 *
 * The chat panel re-emits the pending proposal on every message refetch, so an
 * incoming value only replaces the current one when the agent actually changed
 * it — otherwise a refetch would clobber the user's edit mid-review.
 */
export default function useProposalCommitMessage() {
  const [commitMessage, setCommitMessage] = useState<string | null>(null);
  const fromProposalRef = useRef<string | null>(null);

  const receiveCommitMessage = useCallback((incoming?: string) => {
    const next = incoming ?? null;
    if (fromProposalRef.current === next) return;
    fromProposalRef.current = next;
    setCommitMessage(next);
  }, []);

  const resetCommitMessage = useCallback(() => {
    fromProposalRef.current = null;
    setCommitMessage(null);
  }, []);

  return {
    commitMessage,
    setCommitMessage,
    receiveCommitMessage,
    resetCommitMessage,
  };
}
