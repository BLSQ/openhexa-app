import { base64ToString } from "webapps/helpers/base64";

const IMAGE_MIME_BY_EXT: Record<string, string> = {
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  gif: "image/gif",
  webp: "image/webp",
  bmp: "image/bmp",
  ico: "image/x-icon",
  avif: "image/avif",
};

export const getImageMimeType = (path: string): string | null => {
  const ext = path.split(".").pop()?.toLowerCase();
  return ext ? (IMAGE_MIME_BY_EXT[ext] ?? null) : null;
};

export const decodeFileContent = (path: string, base64: string): string => {
  const mime = getImageMimeType(path);
  if (mime) {
    return `data:${mime};base64,${base64}`;
  }
  return base64ToString(base64);
};

export const isImageDataUrl = (content: string): boolean =>
  /^data:image\/[a-z0-9+.-]+;base64,/i.test(content);
