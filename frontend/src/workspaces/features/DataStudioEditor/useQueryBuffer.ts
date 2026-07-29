import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { readScratch, writeScratch } from "./dataStudioScratch";

type UseQueryBufferArgs = {
  // Absent only if the session has no resolved user; the draft is then not
  // cached at all rather than cached unscoped.
  userId?: string;
  workspaceSlug: string;
  savedQuery?: { content: string } | null;
};

// `localStorage.setItem` is synchronous and disk-backed, and a draft runs to
// MAX_LENGTH, so mirroring per keystroke costs input latency on a large query.
// Short enough that the flushes below cover any realistic way out of the page.
const MIRROR_DELAY_MS = 400;

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
  // Content owed to storage, and the timer that will write it. `null` means
  // nothing is owed, so an empty draft is still a value worth flushing.
  const pendingRef = useRef<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  // Null while there is nothing to mirror to, which keeps the guard in one place
  // and lets the rest of the hook treat the scope as present.
  const scope = useMemo(
    () => (isScratch && userId ? { userId, workspaceSlug } : null),
    [isScratch, userId, workspaceSlug],
  );

  // Restored after mount rather than in the initial state, so the server and
  // the client render the same thing.
  useEffect(() => {
    if (!scope) {
      return;
    }
    const draft = readScratch(scope);
    if (draft) {
      setContent(draft);
    }
  }, [scope]);

  const flush = useCallback(() => {
    clearTimeout(timerRef.current);
    if (!scope || pendingRef.current === null) {
      return;
    }
    const pending = pendingRef.current;
    pendingRef.current = null;
    writeScratch(scope, pending);
  }, [scope]);

  useEffect(() => {
    if (!scope || !editedRef.current) {
      return;
    }
    pendingRef.current = content;
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(flush, MIRROR_DELAY_MS);
  }, [content, flush, scope]);

  // A debounced write must not be what the user loses by leaving, so every exit
  // path flushes it: `pagehide` for tab close and reload (and mobile Safari,
  // where `beforeunload` never fires), `visibilitychange` for a backgrounded tab
  // the browser may then discard, and unmount for in-app navigation, which
  // triggers no page lifecycle event at all.
  useEffect(() => {
    const flushWhenHidden = () => {
      if (document.visibilityState === "hidden") {
        flush();
      }
    };

    window.addEventListener("pagehide", flush);
    document.addEventListener("visibilitychange", flushWhenHidden);

    return () => {
      window.removeEventListener("pagehide", flush);
      document.removeEventListener("visibilitychange", flushWhenHidden);
      flush();
    };
  }, [flush]);

  const edit = useCallback((next: string) => {
    editedRef.current = true;
    setContent(next);
  }, []);

  return [content, edit] as const;
};
