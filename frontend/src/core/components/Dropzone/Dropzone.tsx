import {
  ExclamationTriangleIcon,
  ArrowUpTrayIcon,
} from "@heroicons/react/24/solid";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { ReactNode, useState } from "react";
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
  const [inputKey] = useState("");
  const [acceptedFilesMap, setAcceptedFilesMap] = useState<
    Map<string, FileWithPath>
  >(new Map());
  const acceptedFiles = Array.from<File>(acceptedFilesMap.values());
  const { getInputProps, getRootProps, fileRejections, isDragAccept } =
    useDropzone({
      validator,
      accept,
      maxFiles,
      disabled,
      useFsAccessApi: false,
      multiple: maxFiles !== 1,
      onDrop: (newAcceptedFiles, fileRejections) => {
        const newAcceptedFilesMap = new Map(acceptedFilesMap);
        newAcceptedFiles.forEach(
          (file) => newAcceptedFilesMap.set(file.name, file), //  Ignore duplicates by names
        );
        setAcceptedFilesMap(newAcceptedFilesMap);
        onChange(
          Array.from<File>(newAcceptedFilesMap.values()),
          fileRejections,
        );
      },
    });

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
        "flex w-full cursor-pointer items-center justify-center gap-3 rounded-md border-2 border-dashed border-blue-500 px-5 py-5 text-sm text-gray-500 shadow-xs hover:border-blue-700",
        isDragAccept && "bg-blue-100",
        className,
      )}
      {...getRootProps()}
    >
      <input key={inputKey} {...getInputProps()} />
      {fileRejections.length + acceptedFiles.length === 0 && children}
      {acceptedFiles.length > 0 && (
        <span className="line-clamp-4 text-xs">
          <p>
            {acceptedFiles.length} {pluralize("file", acceptedFiles.length)}{" "}
            selected:{" "}
          </p>
          <ul>
            {acceptedFiles.map((f) => (
              <li key={f.name}>
                <p className="inline">{f.name} - </p>
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
