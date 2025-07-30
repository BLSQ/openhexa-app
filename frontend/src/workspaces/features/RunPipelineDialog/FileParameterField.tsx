import { FolderIcon, XMarkIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Input from "core/components/forms/Input";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import FileBrowserDialog from "../FileBrowserDialog";
import { FileBrowserDialog_BucketObjectFragment } from "../FileBrowserDialog/FileBrowserDialog.generated";

interface FileParameterFieldProps {
  workspaceSlug: string;
  value: string | null;
  onChange: (file: FileBrowserDialog_BucketObjectFragment | null) => void;
  parameter: {
    code: string;
    required?: boolean;
  };
}

const FileParameterField: React.FC<FileParameterFieldProps> = ({
  workspaceSlug,
  value,
  onChange,
  parameter,
}) => {
  const { t } = useTranslation();
  const [modalOpen, setModalOpen] = useState(false);

  const handleSelect = (file: FileBrowserDialog_BucketObjectFragment) => {
    onChange(file);
    setModalOpen(false);
  };

  const handleClear = () => {
    onChange(null);
  };

  return (
    <div className="flex space-x-2">
      <div className="flex-1 cursor-pointer" onClick={() => setModalOpen(true)}>
        <Input
          fullWidth
          readOnly
          value={value || ""}
          placeholder={t("No file selected")}
          className="cursor-pointer"
          name={parameter.code}
          required={Boolean(parameter.required)}
          data-testid={`${parameter.code}-input`}
          trailingIcon={
            <div className="flex items-center space-x-3">
              {value && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClear();
                  }}
                  className="text-gray-500 hover:text-gray-700 focus:text-gray-700 cursor-pointer"
                  title={t("Clear")}
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              )}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setModalOpen(true);
                }}
                className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 text-sm font-medium cursor-pointer"
              >
                <FolderIcon className="h-4 w-4" />
                <span>{t("Browse")}</span>
              </button>
            </div>
          }
        />
      </div>

      <FileBrowserDialog
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        workspaceSlug={workspaceSlug}
        onSelect={handleSelect}
        selectedFile={value}
      />
    </div>
  );
};

export default FileParameterField;
