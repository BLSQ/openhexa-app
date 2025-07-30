import { FolderIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Input from "core/components/forms/Input";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import FileBrowserModal from "../FileBrowserModal";
import { FileBrowserModal_BucketObjectFragment } from "../FileBrowserModal/FileBrowserModal.generated";

interface FileParameterFieldProps {
  workspaceSlug: string;
  value: string | null;
  onChange: (file: FileBrowserModal_BucketObjectFragment | null) => void;
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

  const handleSelect = (file: FileBrowserModal_BucketObjectFragment) => {
    onChange(file);
    setModalOpen(false);
  };

  const handleClear = () => {
    onChange(null);
  };

  return (
    <div className="flex space-x-2">
      <Input
        fullWidth
        readOnly
        value={value || ""}
        placeholder={t("No file selected")}
        className="flex-1"
        name={parameter.code}
        required={Boolean(parameter.required)}
        data-testid={`${parameter.code}-input`}
      />
      <Button
        type="button"
        variant="outlined"
        onClick={() => setModalOpen(true)}
        leadingIcon={<FolderIcon className="h-4 w-4" />}
      >
        {t("Browse")}
      </Button>
      {value && (
        <Button
          type="button"
          variant="outlined"
          onClick={handleClear}
          className="text-gray-500 hover:text-gray-700"
        >
          {t("Clear")}
        </Button>
      )}

      <FileBrowserModal
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
