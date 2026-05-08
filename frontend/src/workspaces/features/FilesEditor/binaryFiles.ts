const IMAGE_MIME_TYPES: Record<string, string> = {
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  gif: "image/gif",
  webp: "image/webp",
  bmp: "image/bmp",
  ico: "image/x-icon",
  avif: "image/avif",
};

export const getImageMimeType = (filename: string): string | null => {
  const ext = filename.split(".").pop()?.toLowerCase();
  return ext ? (IMAGE_MIME_TYPES[ext] ?? null) : null;
};

