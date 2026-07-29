import { useCallback, useEffect, useRef, useState } from "react";
import { readScratch, writeScratch } from "./dataStudioScratch";

type UseQueryBufferArgs = {
  // Absent only if the session has no resolved user; the draft is then not
  // cached at all rather than cached unscoped.
  userId?: string;
  workspaceSlug: string;
  savedQuery?: { content: string } | null;
};

// Owns the SQL buffer of the editor. A buffer backed by a saved query lives only
// in memory; the scratch buffer of the unsaved editor is mirrored to local
// storage, so navigating away from it does not discard the draft.
export const useQueryBuffer = ({
  userId,
  workspaceSlug,
  savedQuery,
}: UseQueryBufferArgs) => {
  const isScratch = !savedQuery;
  const [content, setContent] = useState(savedQuery?.content ?? "");
  // Only the user's own edits are mirrored: restoring a draft must not write it
  // straight back, and an editor nobody has touched must not clear it.
  const editedRef = useRef(false);

  // Restored after mount rather than in the initial state, so the server and
  // the client render the same thing.
  useEffect(() => {
    if (!isScratch || !userId) {
      return;
    }
    const draft = readScratch({ userId, workspaceSlug });
    if (draft) {
      setContent(draft);
    }
  }, [isScratch, userId, workspaceSlug]);

  // Mirrored on every edit rather than debounced: the write is cheap, and a
  // pending one would be lost precisely when the user leaves in a hurry.
  useEffect(() => {
    if (isScratch && userId && editedRef.current) {
      writeScratch({ userId, workspaceSlug }, content);
    }
  }, [content, isScratch, userId, workspaceSlug]);

  const edit = useCallback((next: string) => {
    editedRef.current = true;
    setContent(next);
  }, []);

  return [content, edit] as const;
};
