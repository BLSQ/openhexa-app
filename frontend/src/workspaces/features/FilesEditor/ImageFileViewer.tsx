type ImageFileViewerProps = {
  filename: string;
  base64: string;
  mimeType: string;
};

const ImageFileViewer = ({
  filename,
  base64,
  mimeType,
}: ImageFileViewerProps) => (
  <div className="flex flex-col items-center justify-center h-full bg-gray-50 p-6 overflow-auto">
    <img
      src={`data:${mimeType};base64,${base64}`}
      alt={filename}
      className="max-w-full max-h-full object-contain shadow-sm rounded-md bg-white"
    />
  </div>
);

export default ImageFileViewer;
