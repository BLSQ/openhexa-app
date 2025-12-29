import React from "react";
import clsx from "clsx";
import { useDropzone, FileWithPath } from "react-dropzone";

interface DropzoneOverlayProps extends React.HTMLAttributes<HTMLDivElement> {
  onDroppingFiles: (files: FileWithPath[]) => void;
}

const DropzoneOverlay: React.FC<DropzoneOverlayProps> = (props) => {
  const { onDroppingFiles, children, className, ...otherDivProps } = props;

  const { getRootProps, isDragActive } = useDropzone({
    onDrop: (files) => onDroppingFiles(files),
    noClick: true,
    useFsAccessApi: false,
  });

  return (
    <div
      {...getRootProps()}
      className={clsx(className, isDragActive && "opacity-20 blur-[1px]")}
      {...otherDivProps}
    >
      {children}
    </div>
  );
};

export default DropzoneOverlay;
