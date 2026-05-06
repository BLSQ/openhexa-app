import { ArrowDownTrayIcon, DocumentIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Filesize from "core/components/Filesize";
import { useTranslation } from "next-i18next";

type BinaryFilePlaceholderProps = {
  filename?: string;
  downloadUrl?: string;
  size?: number | null;
  message?: string;
  className?: string;
};

const BinaryFilePlaceholder = ({
  filename,
  downloadUrl,
  size,
  message,
  className,
}: BinaryFilePlaceholderProps) => {
  const { t } = useTranslation();
  return (
    <div
      className={clsx(
        "flex flex-col items-center justify-center h-full min-h-[200px] bg-gray-50 p-4 text-center",
        className,
      )}
    >
      <DocumentIcon className="w-12 h-12 text-gray-400 mb-3" />
      <div className="text-gray-700 text-sm mb-1">
        {message ?? t("Preview not available")}
      </div>
      {size != null && (
        <div className="text-gray-500 text-xs mb-4">
          <Filesize size={size} />
        </div>
      )}
      {downloadUrl && (
        <a
          href={downloadUrl}
          download={filename}
          className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          <ArrowDownTrayIcon className="h-4 w-4 text-gray-500" />
          {t("Download")}
        </a>
      )}
    </div>
  );
};

export default BinaryFilePlaceholder;
