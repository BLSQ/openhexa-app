import { useHotkeys } from "react-hotkeys-hook";
import { RefObject } from "react";
import { getLink } from "./mapper";
import { useRouter } from "next/router";

type UseSearchHotkeysParams = {
  isOpen: boolean;
  setIsOpen: (value: boolean) => void;
  inputRef: RefObject<HTMLInputElement>;
  data: any;
  highlightedIndex: number;
  setHighlightedIndex: (value: any) => void;
};

const useSearchHotkeys = ({
  isOpen,
  setIsOpen,
  inputRef,
  data,
  highlightedIndex,
  setHighlightedIndex,
}: UseSearchHotkeysParams) => {
  const router = useRouter();
  const { workspaceSlug: currentWorkspaceSlug } = router.query as {
    workspaceSlug: string | undefined;
  };

  // Open and close the search
  useHotkeys(
    "mod+k",
    () => {
      setIsOpen(!isOpen);
    },
    { enableOnFormTags: ["INPUT", "TEXTAREA"] },
  );

  // Close the search when pressing escape
  useHotkeys(
    "esc",
    () => {
      setIsOpen(false);
    },
    { enableOnFormTags: ["INPUT", "TEXTAREA"] },
  );

  // Navigate down the list
  useHotkeys(
    "ArrowDown",
    () => {
      setHighlightedIndex((prev: number) => prev + 1);
    },
    { enableOnFormTags: ["INPUT"], enabled: isOpen },
  );

  // Navigate up the list
  useHotkeys(
    "ArrowUp",
    () => {
      setHighlightedIndex((prev: number) => prev - 1);
    },
    { enableOnFormTags: ["INPUT"], enabled: isOpen },
  );

  // Focus the input box when typing
  useHotkeys(
    "*",
    () => {
      inputRef.current?.focus();
    },
    { enableOnFormTags: ["INPUT"], enabled: isOpen },
  );

  useHotkeys(
    "enter",
    () => {
      const href = getLink(data[highlightedIndex], currentWorkspaceSlug);
      href && router.push(href).then();
    },
    { enableOnFormTags: ["INPUT"], enabled: isOpen },
  );
};

export default useSearchHotkeys;
