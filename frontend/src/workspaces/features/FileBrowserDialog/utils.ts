import {
  BookOpenIcon,
  CodeBracketIcon,
  DocumentArrowDownIcon,
  DocumentIcon,
  DocumentTextIcon,
  PhotoIcon,
  TableCellsIcon,
  FilmIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
} from "@heroicons/react/24/outline";

// File type detection utility based on file extensions
export const getFileIcon = (fileName: string): typeof DocumentIcon => {
  const extension = fileName.toLowerCase().split(".").pop();

  switch (extension) {
    // Notebooks
    case "ipynb":
      return BookOpenIcon;

    // Code files
    case "py":
    case "js":
    case "ts":
    case "tsx":
    case "jsx":
    case "html":
    case "css":
    case "scss":
    case "sass":
    case "json":
    case "xml":
    case "yaml":
    case "yml":
    case "sql":
    case "sh":
    case "bash":
    case "r":
    case "php":
    case "java":
    case "cpp":
    case "c":
    case "h":
    case "go":
    case "rs":
    case "swift":
    case "kt":
    case "rb":
    case "pl":
    case "scala":
    case "clj":
    case "hs":
    case "elm":
    case "dart":
    case "vue":
    case "svelte":
      return CodeBracketIcon;

    // Text files
    case "txt":
    case "md":
    case "rst":
    case "rtf":
    case "log":
      return DocumentTextIcon;

    // Data files
    case "csv":
    case "tsv":
    case "xls":
    case "xlsx":
    case "ods":
      return TableCellsIcon;

    // Images
    case "jpg":
    case "jpeg":
    case "png":
    case "gif":
    case "svg":
    case "webp":
    case "bmp":
    case "tiff":
    case "ico":
      return PhotoIcon;

    // Videos
    case "mp4":
    case "avi":
    case "mov":
    case "wmv":
    case "flv":
    case "webm":
    case "mkv":
    case "m4v":
      return FilmIcon;

    // Audio
    case "mp3":
    case "wav":
    case "flac":
    case "aac":
    case "ogg":
    case "wma":
    case "m4a":
      return MusicalNoteIcon;

    // Archives
    case "zip":
    case "rar":
    case "tar":
    case "gz":
    case "7z":
    case "bz2":
    case "xz":
      return ArchiveBoxIcon;

    // Documents
    case "pdf":
    case "doc":
    case "docx":
    case "odt":
    case "ppt":
    case "pptx":
    case "odp":
      return DocumentArrowDownIcon;

    // Default
    default:
      return DocumentIcon;
  }
};

// Get file type color for better visual distinction
export const getFileIconColor = (fileName: string): string => {
  const extension = fileName.toLowerCase().split(".").pop();

  switch (extension) {
    case "ipynb":
      return "text-orange-500";
    case "py":
      return "text-blue-500";
    case "js":
    case "ts":
    case "tsx":
    case "jsx":
      return "text-yellow-500";
    case "html":
    case "css":
    case "scss":
    case "sass":
      return "text-purple-500";
    case "json":
    case "xml":
    case "yaml":
    case "yml":
      return "text-green-500";
    case "csv":
    case "xlsx":
    case "xls":
      return "text-emerald-500";
    case "jpg":
    case "jpeg":
    case "png":
    case "gif":
    case "svg":
    case "webp":
      return "text-pink-500";
    case "mp4":
    case "avi":
    case "mov":
      return "text-red-500";
    case "mp3":
    case "wav":
    case "flac":
      return "text-indigo-500";
    case "zip":
    case "rar":
    case "tar":
    case "gz":
      return "text-gray-600";
    case "pdf":
    case "doc":
    case "docx":
      return "text-red-600";
    default:
      return "text-gray-400";
  }
};
