import { filesize } from "filesize";
import { useMemo } from "react";
type FilesizeProps = {
  size: number;
  className?: string;
};

const Filesize = (props: FilesizeProps) => {
  const { size, className } = props;

  const humanSize = useMemo(() => {
    return filesize(size, { output: "string" }) as string;
  }, [size]);
  return <span className={className}>{humanSize}</span>;
};

export default Filesize;
