import useCookieState from "core/hooks/useCookieState";

export default function useFilesEditorPanelOpen() {
  return useCookieState<boolean>({
    name: "files-editor-panel-open",
    defaultValue: true,
  });
}