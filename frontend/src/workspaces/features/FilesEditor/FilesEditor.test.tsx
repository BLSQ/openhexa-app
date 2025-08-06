import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { FilesEditor } from "./FilesEditor";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";
import { FileType } from "graphql/types";

const mockFiles: FilesEditor_FileFragment[] = [
  {
    id: "1",
    name: "root",
    path: "/root",
    type: FileType.Directory,
    content: null,
    parentId: null,
    autoSelect: false,
    language: null,
    lineCount: null,
  },
  {
    id: "2",
    name: "file1.py",
    path: "/root/file1.py",
    type: FileType.File,
    content: "print('hello world')",
    parentId: "1",
    autoSelect: true,
    language: "python",
    lineCount: 1,
  },
  {
    id: "3",
    name: "subdirectory",
    path: "/root/subdirectory",
    type: FileType.Directory,
    content: null,
    parentId: "1",
    autoSelect: false,
    language: null,
    lineCount: null,
  },
  {
    id: "4",
    name: "file2.json",
    path: "/root/subdirectory/file2.json",
    type: FileType.File,
    content: '{"key": "value"}',
    parentId: "3",
    autoSelect: false,
    language: "json",
    lineCount: 1,
  },
];

const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

describe("FilesEditor", () => {
  beforeEach(() => {
    localStorageMock.getItem.mockReturnValue(null);
    localStorageMock.setItem.mockClear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders the FilesEditor with file tree and code editor", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    expect(screen.getByText("Files - Test Project")).toBeInTheDocument();
    expect(screen.getByText("4 files")).toBeInTheDocument();
    expect(screen.getByText("root")).toBeInTheDocument();
    expect(screen.getByText("file1.py")).toBeInTheDocument();
  });

  it("shows toggle button for the file panel", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    const toggleButton = screen.getByLabelText("Toggle file panel");
    expect(toggleButton).toBeInTheDocument();
  });

  it("toggles panel state when toggle button is clicked", async () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    const toggleButton = screen.getByLabelText("Toggle file panel");
    const filePanel = screen.getByTestId("file-panel");

    expect(filePanel).toHaveClass("w-80");

    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(filePanel).toHaveClass("w-0");
      expect(filePanel).toHaveClass("overflow-hidden");
    });

    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      "files-editor-panel-open",
      "false",
    );
  });


  it("loads state from localStorage on mount", async () => {
    localStorageMock.getItem.mockReturnValue("false");

    render(<FilesEditor name="Test Project" files={mockFiles} />);

    await waitFor(() => {
      const filePanel = screen.getByTestId("file-panel");
      expect(filePanel).toHaveClass("w-0");
    });

    expect(localStorageMock.getItem).toHaveBeenCalledWith(
      "files-editor-panel-open",
    );
  });


  it("expands directory nodes when clicked", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    const rootDirectory = screen.getByText("root");
    fireEvent.click(rootDirectory);

    expect(screen.getByText("subdirectory")).toBeInTheDocument();
  });

  it("selects files when clicked", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    const rootDirectory = screen.getByText("root");
    fireEvent.click(rootDirectory);

    const file = screen.getByText("file1.py");
    fireEvent.click(file);

    expect(screen.getByText("print('hello world')")).toBeInTheDocument();
  });

  it("displays empty state when no file is selected", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    expect(screen.getByText("Select a file to view")).toBeInTheDocument();
    expect(
      screen.getByText("Choose a file from the sidebar to view its contents"),
    ).toBeInTheDocument();
  });
});