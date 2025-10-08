import {
  ArchiveBoxIcon,
  BookOpenIcon,
  CodeBracketIcon,
  DocumentArrowDownIcon,
  DocumentIcon,
  DocumentTextIcon,
  FilmIcon,
  MusicalNoteIcon,
  PhotoIcon,
  TableCellsIcon,
} from "@heroicons/react/24/outline";

const FILE_TYPES = {
  notebooks: {
    extensions: ["ipynb"],
    icon: BookOpenIcon,
    color: "text-orange-500",
  },
  code: {
    extensions: [
      "py",
      "js",
      "ts",
      "tsx",
      "jsx",
      "html",
      "css",
      "scss",
      "sass",
      "json",
      "xml",
      "yaml",
      "yml",
      "sql",
      "sh",
      "bash",
      "r",
      "php",
      "java",
      "cpp",
      "c",
      "h",
      "go",
      "rs",
      "swift",
      "kt",
      "rb",
      "pl",
      "scala",
      "clj",
      "hs",
      "elm",
      "dart",
      "vue",
      "svelte",
    ],
    icon: CodeBracketIcon,
    color: "text-blue-500",
  },
  text: {
    extensions: ["txt", "md", "rst", "rtf", "log"],
    icon: DocumentTextIcon,
    color: "text-gray-400",
  },
  spreadsheet: {
    extensions: ["csv", "xlsx", "xls", "tsv", "ods", "parquet"],
    icon: TableCellsIcon,
    color: "text-emerald-500",
  },
  images: {
    extensions: [
      "jpg",
      "jpeg",
      "png",
      "gif",
      "svg",
      "webp",
      "bmp",
      "tiff",
      "ico",
    ],
    icon: PhotoIcon,
    color: "text-pink-500",
  },
  videos: {
    extensions: ["mp4", "avi", "mov", "wmv", "flv", "webm", "mkv", "m4v"],
    icon: FilmIcon,
    color: "text-red-500",
  },
  audio: {
    extensions: ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a"],
    icon: MusicalNoteIcon,
    color: "text-indigo-500",
  },
  archives: {
    extensions: ["zip", "rar", "tar", "gz", "7z", "bz2", "xz"],
    icon: ArchiveBoxIcon,
    color: "text-gray-600",
  },
  documents: {
    extensions: ["pdf", "doc", "docx", "odt", "ppt", "pptx", "odp"],
    icon: DocumentArrowDownIcon,
    color: "text-red-600",
  },
};

// flat extension lookup map for O(1) access
const EXTENSION_LOOKUP_MAP = Object.values(FILE_TYPES).reduce((acc, fileType) => {
  fileType.extensions.forEach(extension => {
    acc[extension] = { icon: fileType.icon, color: fileType.color };
  });
  return acc;
}, {} as Record<string, { icon: any; color: string }>);

// Get file icon and color based on file extension
export const getFileIconAndColor = (fileName: string) => {
  const extension = fileName.toLowerCase().split(".").pop();

  if (extension && EXTENSION_LOOKUP_MAP[extension]) {
    return EXTENSION_LOOKUP_MAP[extension];
  }

  return { icon: DocumentIcon, color: "text-gray-400" };
};
