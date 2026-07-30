import { useCallback, useRef } from "react";
import useEventListener from "./useEventListener";

/**
 * Runs `onSave` on ⌘S (macOS) / Ctrl+S, and suppresses the browser's
 * "Save page as…" dialog.
 *
 * Bound on the window rather than in an editor's own keymap: saving is a
 * page-level command that must work wherever focus sits, and a second binding
 * inside CodeMirror would fire on top of this one — its `preventDefault` stops
 * the browser default but not the event from reaching the window — saving twice.
 *
 * @example useSaveShortcut(editor.commit, !editor.dialog)
 */
const useSaveShortcut = (onSave: () => void, enabled = true) => {
  // Hold the latest callback in a ref: save handlers typically close over the
  // editor buffer, so depending on its identity would re-subscribe the window
  // listener on every keystroke.
  const onSaveRef = useRef(onSave);
  onSaveRef.current = onSave;

  const onKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled || event.key.toLowerCase() !== "s") {
        return;
      }
      if (!(event.metaKey || event.ctrlKey) || event.altKey || event.shiftKey) {
        return;
      }
      // Consumed even when the save turns out to be a no-op, so the browser
      // never takes over the keystroke while the user is in an editor.
      event.preventDefault();
      onSaveRef.current();
    },
    [enabled],
  );

  useEventListener("keydown", onKeyDown);
};

export default useSaveShortcut;
