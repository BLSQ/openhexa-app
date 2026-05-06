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

const getImageMimeType = (path: string): string | null => {
  const ext = path.split(".").pop()?.toLowerCase();
  return ext ? (IMAGE_MIME_BY_EXT[ext] ?? null) : null;
};

export const decodeFileContent = (
  path: string,
  base64: string | null | undefined,
  language: string | null | undefined,
): string | null => {
  if (base64 == null) return null;
  if (language) {
    return base64ToString(base64);
  }
  const mime = getImageMimeType(path) ?? "application/octet-stream";
  return `data:${mime};base64,${base64}`;
};
