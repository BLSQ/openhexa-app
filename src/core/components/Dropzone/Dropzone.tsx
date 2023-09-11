import {
  ExclamationTriangleIcon,
  ArrowUpTrayIcon,
} from "@heroicons/react/24/solid";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { ReactNode, useEffect, useState } from "react";
import type { Accept, FileError, FileRejection } from "react-dropzone";
import { useDropzone } from "react-dropzone";
import Button from "../Button";

export type DropzoneProps = {
  className?: string;
  label?: ReactNode;
  help?: ReactNode;
  accept?: Accept;
  disabled?: boolean;
  children?: ReactNode;
  maxFiles?: number;
  onChange: <T extends File>(
    acceptedFiles: T[],
    rejectedFiles: FileRejection[],
  ) => void;
  validator?: <T extends File>(file: T) => FileError | FileError[] | null;
};

const Dropzone = (props: DropzoneProps) => {
  const {
    className,
    help,
    label,
    validator,
    disabled,
    accept,
    maxFiles = 0,
    onChange,
  } = props;
  const { t } = useTranslation();
  const [isMounted, setMounted] = useState(false);
  const [inputKey, setInputKey] = useState("");
  const { getInputProps, getRootProps, acceptedFiles, fileRejections } =
    useDropzone({
      validator,
      accept,
      maxFiles,
      disabled,
      useFsAccessApi: false,
      multiple: maxFiles !== 1,
    });

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (isMounted) {
      onChange(acceptedFiles, fileRejections);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [acceptedFiles, fileRejections]);

  const children = props.children ?? (
    <>
      <div className="flex items-center gap-1">
        <ArrowUpTrayIcon className="h-4 w-4" />
        <div>{label}</div>
      </div>
      {help && <div className="italic text-gray-600">{help}</div>}
    </>
  );

  return (
    <div
      className={clsx(
        "flex w-full cursor-pointer items-center justify-center gap-3 rounded-md border-2 border-dashed border-blue-500 px-5 py-5 text-sm text-gray-500 shadow-sm hover:border-blue-700",
        className,
      )}
      {...getRootProps()}
    >
      <input key={inputKey} {...getInputProps()} />
      {fileRejections.length + acceptedFiles.length === 0 && children}
      {acceptedFiles.length > 0 && (
        <span className="line-clamp-3 text-xs">
          {acceptedFiles?.map((f) => f.name).join(", ")}
        </span>
      )}
      {fileRejections?.length > 0 && (
        <div className="flex items-center">
          <ExclamationTriangleIcon className="mr-1 h-4 text-amber-400" />
          <span className="font-semibold">
            {t("{{files}} is not a valid file", {
              count: fileRejections.length,
              files: fileRejections
                .map((rejection) => rejection.file.name)
                .join(", "),
            })}
          </span>
        </div>
      )}
    </div>
  );
};

export default Dropzone;
