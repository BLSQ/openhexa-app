// Mirrors hexa.files.utils.PUBLIC_FOLDER: the bucket's top-level folder whose
// files anyone can read once the workspace has public files enabled.
export const PUBLIC_FOLDER = "public";

const PUBLIC_PREFIX = `${PUBLIC_FOLDER}/`;

// Bucket listings name a directory with or without its trailing slash depending
// on the storage backend, so both spellings are the public folder.
export const isPublicFolder = (key: string) =>
  key.replace(/\/$/, "") === PUBLIC_FOLDER;

export const isInPublicFolder = (key: string) => key.startsWith(PUBLIC_PREFIX);

// The stable, anonymous URL of a file: `publicFilesUrl` is the workspace's base
// (ending with a slash) and the key keeps its slashes while every other
// character that could break a URL is escaped.
export const getPublicFileUrl = (publicFilesUrl: string, key: string) =>
  publicFilesUrl + key.split("/").map(encodeURIComponent).join("/");
