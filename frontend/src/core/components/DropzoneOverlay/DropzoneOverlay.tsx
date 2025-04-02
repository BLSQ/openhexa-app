import React, { useState, DragEvent } from "react";
import clsx from "clsx";

interface DropzoneOverlayProps extends React.HTMLAttributes<HTMLDivElement> {
  onDroppingFiles: (files: File[]) => void;
}

const DropzoneOverlay: React.FC<DropzoneOverlayProps> = (props) => {
  const { onDroppingFiles, ...otherDivProps } = props;
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files: File[] = Array.from(e.dataTransfer.files);
    if (onDroppingFiles && files.length > 0) {
      onDroppingFiles(files);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={clsx(isDragging && "opacity-20 blur-[1px]")}
      {...otherDivProps}
    />
  );
};

export default DropzoneOverlay;
