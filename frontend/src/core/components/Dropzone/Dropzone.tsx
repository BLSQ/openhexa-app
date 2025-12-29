import {
  ExclamationTriangleIcon,
  ArrowUpTrayIcon,
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
  const acceptedFiles = Array.from<FileWithPath>(acceptedFilesMap.values());

  const addFiles = (
    files: FileWithPath[],
    rejections: FileRejection[] = [],
  ) => {
    const newMap = new Map(acceptedFilesMap);
    files.forEach((f) =>
      newMap.set(f.path ?? f.webkitRelativePath ?? f.name, f),
    );
    setAcceptedFilesMap(newMap);
    onChange(Array.from(newMap.values()), rejections);
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
            addFiles(Array.from(e.target.files) as FileWithPath[]);
          }
        }}
        {...({
          webkitdirectory: "",
        } as InputHTMLAttributes<HTMLInputElement>)}
      />
      {fileRejections.length + acceptedFiles.length === 0 && children}
      {acceptedFiles.length > 0 && (
        <span className="line-clamp-4 text-xs">
          <p>
            {acceptedFiles.length} {pluralize("file", acceptedFiles.length)}{" "}
            selected:{" "}
          </p>
          <ul>
            {acceptedFiles.map((f) => (
              <li key={f.path ?? f.webkitRelativePath ?? f.name}>
                <p className="inline">
                  {f.path ?? f.webkitRelativePath ?? f.name} -{" "}
                </p>
                <Filesize className="inline" size={f.size} />
              </li>
            ))}
          </ul>
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
