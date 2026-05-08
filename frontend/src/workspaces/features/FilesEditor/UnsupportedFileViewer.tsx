import { DocumentIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";

const UnsupportedFileViewer = () => {
  const { t } = useTranslation();
  return (
    <div className="flex items-center justify-center h-full bg-gray-50 p-6">
      <div className="text-center max-w-sm">
        <DocumentIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <div className="text-gray-700 text-sm font-medium">
          {t("This file can't be displayed")}
        </div>
      </div>
    </div>
  );
};

export default UnsupportedFileViewer;
