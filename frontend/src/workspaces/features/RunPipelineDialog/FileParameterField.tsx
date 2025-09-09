import { useCallback, useState } from "react";
import { FolderIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";

import Input from "core/components/forms/Input";

import FileBrowserDialog from "../FileBrowserDialog";
import { FileBrowserDialog_BucketObjectFragment } from "../FileBrowserDialog/FileBrowserDialog.generated";

type FileParameterFieldProps = {
  workspaceSlug: string;
  value: string | null;
  onChange: (file: FileBrowserDialog_BucketObjectFragment | null) => void;
  parameter: {
    code: string;
    required?: boolean;
  };
};

const FileParameterField = (props: FileParameterFieldProps) => {
  const { workspaceSlug, value, onChange, parameter } = props;
  const { t } = useTranslation();
  const [modalOpen, setModalOpen] = useState(false);

  const handleSelectFile = useCallback(
    (file: FileBrowserDialog_BucketObjectFragment) => {
      onChange(file);
      setModalOpen(false);
    },
    [onChange, setModalOpen],
  );

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
                  <XMarkIcon className="h-6 w-6 mr-3" />
                </button>
              )}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setModalOpen(true);
                }}
                className="flex items-center mr-3 space-x-1 text-sm font-medium cursor-pointer"
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
        onSelectFile={handleSelectFile}
      />
    </div>
  );
};

export default FileParameterField;
