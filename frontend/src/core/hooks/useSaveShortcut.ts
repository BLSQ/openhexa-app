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
 * The keystroke is unconditionally consumed and `onSave` decides whether there
 * is anything to do. A state where saving is a no-op must still not hand ⌘S
 * back to the browser, or the user gets "Save page as…" instead of nothing.
 *
 * @example useSaveShortcut(editor.commit)
 */
const useSaveShortcut = (onSave: () => void) => {
  // Hold the latest callback in a ref: save handlers typically close over the
  // editor buffer, so depending on its identity would re-subscribe the window
  // listener on every keystroke.
  const onSaveRef = useRef(onSave);
  onSaveRef.current = onSave;

  const onKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key.toLowerCase() !== "s") {
      return;
    }
    if (!(event.metaKey || event.ctrlKey) || event.altKey || event.shiftKey) {
      return;
    }
    event.preventDefault();
    // Auto-repeat fires every few dozen milliseconds while the key is held,
    // which outpaces the re-render that flips the in-flight flag `onSave`
    // guards on — one held keystroke would dispatch several saves.
    if (event.repeat) {
      return;
    }
    onSaveRef.current();
  }, []);

  useEventListener("keydown", onKeyDown);
};

export default useSaveShortcut;
