import { CheckIcon, ClipboardDocumentIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "next-i18next";

interface ClipboardProps {
  value: string;
  iconClassName?: string;
  children?: React.ReactNode;
}

const Clipboard = (props: ClipboardProps) => {
  const { value, children, iconClassName = "h-4 w-4" } = props;
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const handleClick = useCallback(() => {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
    });
  }, [value]);

  useEffect(() => {
    let timeout: NodeJS.Timeout | undefined;
    if (copied) {
      timeout = setTimeout(() => {
        setCopied((copied) => !copied);
      }, 2000);
    }
    return () => timeout && clearTimeout(timeout);
  }, [copied]);

  const icon = (
    <button
      title={t("Copy")}
      type="button"
      onClick={handleClick}
      className="rounded-sm opacity-90 transition-opacity hover:opacity-100 focus:outline-hidden focus:ring-2 focus:ring-offset-2"
    >
      {!copied ? (
        <ClipboardDocumentIcon className={iconClassName} />
      ) : (
        <CheckIcon className={clsx(iconClassName, "text-green-600")} />
      )}
    </button>
  );

  if (children) {
    return (
      <div className={"flex items-center gap-2"}>
        {children}
        {icon}
      </div>
    );
  } else {
    return icon;
  }
};

export default Clipboard;
