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

const FILE_TYPES = {
  notebooks: {
    extensions: ["ipynb"],
    icon: BookOpenIcon,
    color: "text-orange-500"
  },
  python: {
    extensions: ["py"],
    icon: CodeBracketIcon,
    color: "text-blue-500"
  },
  javascript: {
    extensions: ["js", "ts", "tsx", "jsx"],
    icon: CodeBracketIcon,
    color: "text-yellow-500"
  },
  web: {
    extensions: ["html", "css", "scss", "sass"],
    icon: CodeBracketIcon,
    color: "text-purple-500"
  },
  data: {
    extensions: ["json", "xml", "yaml", "yml"],
    icon: CodeBracketIcon,
    color: "text-green-500"
  },
  code: {
    extensions: ["sql", "sh", "bash", "r", "php", "java", "cpp", "c", "h", "go", "rs", "swift", "kt", "rb", "pl", "scala", "clj", "hs", "elm", "dart", "vue", "svelte"],
    icon: CodeBracketIcon,
    color: "text-gray-400"
  },
  text: {
    extensions: ["txt", "md", "rst", "rtf", "log"],
    icon: DocumentTextIcon,
    color: "text-gray-400"
  },
  spreadsheet: {
    extensions: ["csv", "xlsx", "xls"],
    icon: TableCellsIcon,
    color: "text-emerald-500"
  },
  data_files: {
    extensions: ["tsv", "ods"],
    icon: TableCellsIcon,
    color: "text-gray-400"
  },
  images: {
    extensions: ["jpg", "jpeg", "png", "gif", "svg", "webp"],
    icon: PhotoIcon,
    color: "text-pink-500"
  },
  image_files: {
    extensions: ["bmp", "tiff", "ico"],
    icon: PhotoIcon,
    color: "text-gray-400"
  },
  videos: {
    extensions: ["mp4", "avi", "mov"],
    icon: FilmIcon,
    color: "text-red-500"
  },
  video_files: {
    extensions: ["wmv", "flv", "webm", "mkv", "m4v"],
    icon: FilmIcon,
    color: "text-gray-400"
  },
  audio: {
    extensions: ["mp3", "wav", "flac"],
    icon: MusicalNoteIcon,
    color: "text-indigo-500"
  },
  audio_files: {
    extensions: ["aac", "ogg", "wma", "m4a"],
    icon: MusicalNoteIcon,
    color: "text-gray-400"
  },
  archives: {
    extensions: ["zip", "rar", "tar", "gz"],
    icon: ArchiveBoxIcon,
    color: "text-gray-600"
  },
  archive_files: {
    extensions: ["7z", "bz2", "xz"],
    icon: ArchiveBoxIcon,
    color: "text-gray-400"
  },
  documents: {
    extensions: ["pdf", "doc", "docx"],
    icon: DocumentArrowDownIcon,
    color: "text-red-600"
  },
  document_files: {
    extensions: ["odt", "ppt", "pptx", "odp"],
    icon: DocumentArrowDownIcon,
    color: "text-gray-400"
  }
};

const getFileType = (fileName: string) => {
  const extension = fileName.toLowerCase().split(".").pop();
  
  for (const fileType of Object.values(FILE_TYPES)) {
    if (fileType.extensions.includes(extension)) {
      return fileType;
    }
  }
  
  return { icon: DocumentIcon, color: "text-gray-400" };
};

// File type detection utility based on file extensions
export const getFileIcon = (fileName: string): typeof DocumentIcon => {
  return getFileType(fileName).icon;
};

// Get file type color for better visual distinction
export const getFileIconColor = (fileName: string): string => {
  return getFileType(fileName).color;
};
