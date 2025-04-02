import { FC, useCallback, useEffect, useRef, useState } from "react";

interface IframeProps extends React.IframeHTMLAttributes<HTMLIFrameElement> {
  autoResize?: boolean;
}

const Iframe: FC<IframeProps> = ({ onLoad, autoResize = false, ...props }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [dimensions, setDimensions] = useState<{
    width: number;
    height: number;
  }>({
    width: 0,
    height: 0,
  });

  useEffect(() => {
    if (!iframeRef.current || !autoResize) return;

    const resizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });

    resizeObserver.observe(iframeRef.current.parentElement!);

    return () => {
      resizeObserver.disconnect();
    };
  }, [autoResize]);

  return (
    <iframe
      ref={iframeRef}
      loading="lazy"
      width={autoResize ? dimensions.width || props.width : props.width}
      height={autoResize ? dimensions.height || props.height : props.height}
      {...props}
    />
  );
};

export default Iframe;
