import {
  ExclamationTriangleIcon,
  ArrowUpTrayIcon,
  DocumentIcon,
  XMarkIcon,
} from "@heroicons/react/24/solid";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { InputHTMLAttributes, ReactNode, useRef, useState } from "react";
import type {
  Accept,
  FileError,
  FileRejection,
  FileWithPath,
} from "react-dropzone";
import { useDropzone } from "react-dropzone";
import Filesize from "../Filesize";
import pluralize from "pluralize";

export type DropzoneProps = {
  className?: string;
  label?: ReactNode;
  help?: ReactNode;
  accept?: Accept;
  disabled?: boolean;
  children?: ReactNode;
  maxFiles?: number;
  onChange: <T extends File>(
    acceptedFiles: readonly T[],
    rejectedFiles: readonly FileRejection[],
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
  const folderInputRef = useRef<HTMLInputElement>(null);
  const [acceptedFilesMap, setAcceptedFilesMap] = useState<
    Map<string, FileWithPath>
  >(new Map());
  const acceptedFiles = Array.from<File>(acceptedFilesMap.values());

  const getFileKey = (f: FileWithPath) =>
    f.path || f.webkitRelativePath || f.name;

  const addFiles = (
    files: FileWithPath[],
    rejections: FileRejection[] = [],
  ) => {
    const newMap = new Map(acceptedFilesMap);
    files.forEach((f) => newMap.set(getFileKey(f), f)); // Ignore duplicates by name
    setAcceptedFilesMap(newMap);
    onChange(Array.from(newMap.values()), rejections);
  };

  const removeFile = (key: string) => {
    const newMap = new Map(acceptedFilesMap);
    newMap.delete(key);
    setAcceptedFilesMap(newMap);
    onChange(Array.from(newMap.values()), []);
  };

  const { getInputProps, getRootProps, fileRejections, isDragAccept, open } =
    useDropzone({
      noClick: true,
      validator,
      accept,
      maxFiles,
      disabled,
      useFsAccessApi: false,
      multiple: maxFiles !== 1,
      onDrop: addFiles,
    });

  const children = props.children ?? (
    <div className="flex flex-col items-center gap-1">
      <div className="flex items-center gap-1">
        <ArrowUpTrayIcon className="h-4 w-4" />
        <div>{label}</div>
      </div>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="cursor-pointer text-blue-600 underline hover:text-blue-800"
          onClick={open}
        >
          {t("Select files")}
        </button>
        <span>{t("or")}</span>
        <button
          type="button"
          className="cursor-pointer text-blue-600 underline hover:text-blue-800"
          onClick={() => folderInputRef.current?.click()}
        >
          {t("Select a folder")}
        </button>
      </div>
      {help && <div className="italic text-gray-600">{help}</div>}
    </div>
  );

  return (
    <div
      className={clsx(
        "flex w-full items-center justify-center gap-3 rounded-md border-2 border-dashed px-5 py-5 text-sm text-gray-500 shadow-xs",
        isDragAccept && "border-blue-500 bg-blue-100",
        className,
      )}
      {...getRootProps()}
    >
      <input {...getInputProps()} />
      <input
        ref={folderInputRef}
        type="file"
        multiple
        hidden
        onChange={(e) => {
          if (e.target.files) {
            const filesWithPath = Array.from(e.target.files).map((file) =>
              Object.assign(file, {
                path: file.webkitRelativePath || file.name,
              }),
            );
            addFiles(filesWithPath);
          }
        }}
        {...({
          webkitdirectory: "",
        } as InputHTMLAttributes<HTMLInputElement>)} // Allow folder selection
      />
      {fileRejections.length + acceptedFiles.length === 0 && children}
      {acceptedFiles.length > 0 && (
        <div className="w-full space-y-2">
          <p className="text-center text-xs text-gray-500">
            {acceptedFiles.length} {pluralize("file", acceptedFiles.length)}{" "}
            {t("selected")}
          </p>
          <ul className="max-h-40 space-y-1 overflow-y-auto">
            {acceptedFiles.map((f) => {
              const key = getFileKey(f);
              return (
                <li
                  key={key}
                  className="flex items-center gap-2 rounded bg-gray-50 px-2 py-1"
                >
                  <DocumentIcon className="h-4 w-4 shrink-0 text-gray-400" />
                  <span className="min-w-0 flex-1 truncate text-xs" title={key}>
                    {key}
                  </span>
                  <Filesize
                    className="shrink-0 text-xs text-gray-400"
                    size={f.size}
                  />
                  <button
                    type="button"
                    onClick={() => removeFile(key)}
                    className="shrink-0 rounded p-0.5 text-gray-400 hover:bg-gray-200 hover:text-gray-600"
                  >
                    <XMarkIcon className="h-3 w-3" />
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
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
