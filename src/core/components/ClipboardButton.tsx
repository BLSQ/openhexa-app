import {
  CheckBadgeIcon,
  CheckIcon,
  ClipboardDocumentCheckIcon,
  ClipboardDocumentIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useCallback, useEffect, useState } from "react";

interface ClipboardButtonProps {
  value: string;
  className?: string;
}

const ClipboardButton = (props: ClipboardButtonProps) => {
  const { value, className = "h-4 w-4" } = props;
  const [copied, setCopied] = useState(false);
  const handleClick = useCallback(() => {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
    });
  }, [value]);

  useEffect(() => {
    if (copied) {
      setTimeout(() => {
        setCopied((copied) => !copied);
      }, 2000);
    }
  }, [copied]);

  return copied ? (
    <button>
      <CheckIcon className={clsx(className, "text-green-800")} />
    </button>
  ) : (
    <button onClick={handleClick}>
      <ClipboardDocumentIcon className={className} />
    </button>
  );
};

export default ClipboardButton;
