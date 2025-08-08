import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { FilesEditor } from "./FilesEditor";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";
import { FileType } from "graphql/types";
import * as cookiesNext from "cookies-next";
import mockRouter from "next-router-mock";

jest.mock("cookies-next", () => ({
  setCookie: jest.fn(),
  getCookie: jest.fn(),
  hasCookie: jest.fn(),
}));

const mockSetCookie = jest.mocked(cookiesNext.setCookie);
const mockGetCookie = jest.mocked(cookiesNext.getCookie);
const mockHasCookie = jest.mocked(cookiesNext.hasCookie);

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
    autoSelect: false,
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

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (str: string) => str,
    i18n: { changeLanguage: jest.fn() },
  }),
}));

const mockOnChange = jest.fn();
jest.mock("@uiw/react-codemirror", () => {
  return function MockCodeMirror({ value, onChange, readOnly }: any) {
    mockOnChange.mockImplementation(onChange);
    return (
      <div data-testid="code-mirror">
        <textarea
          data-testid="code-editor"
          value={value}
          onChange={(e) => onChange && onChange(e.target.value)}
          readOnly={readOnly}
        />
      </div>
    );
  };
});

describe("FilesEditor", () => {
  beforeEach(() => {
    mockHasCookie.mockReturnValue(false);
    mockGetCookie.mockReturnValue("true");
    mockSetCookie.mockClear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders the FilesEditor with file tree and code editor", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    expect(screen.getByText("Files - Test Project")).toBeInTheDocument();
    expect(screen.getByText("2 files")).toBeInTheDocument();
    expect(screen.getByText("root")).toBeInTheDocument();
  });

  it("shows toggle button for the file panel", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    const toggleButton = screen.getByLabelText("Toggle file panel");
    expect(toggleButton).toBeInTheDocument();
  });

  it("toggles panel state when toggle button is clicked", async () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    const toggleButton = screen.getByLabelText("Toggle file panel");
    const filePanel = screen.getByTestId("files-panel");

    expect(filePanel).toBeInTheDocument();

    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(screen.queryByTestId("files-panel")).not.toBeInTheDocument();
    });

    expect(mockSetCookie).toHaveBeenCalledWith(
      "files-editor-panel-open",
      false,
    );
  });

  it("loads state from cookie on mount", async () => {
    mockHasCookie.mockReturnValue(true);
    mockGetCookie.mockReturnValue("false");

    render(<FilesEditor name="Test Project" files={mockFiles} />);

    await waitFor(() => {
      expect(screen.queryByTestId("files-panel")).not.toBeInTheDocument();
    });
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

    expect(screen.getByText(/hello world/i)).toBeInTheDocument();
  });

  it("displays empty state when no file is selected", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    expect(screen.getByText("Select a file to view")).toBeInTheDocument();
    expect(
      screen.getByText("Choose a file from the sidebar to view its contents"),
    ).toBeInTheDocument();
  });

  it("shows file info when a file is selected", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    fireEvent.click(screen.getByText("root"));
    fireEvent.click(screen.getByText("file1.py"));

    expect(screen.getByText(/python/i)).toBeInTheDocument();
    expect(screen.getByText(/1\s+line/)).toBeInTheDocument();
  });

  it("displays modified indicator when file is changed in editable mode and call save action on save", async () => {
    const mockOnSave = jest.fn().mockResolvedValue({ success: true });

    render(
      <FilesEditor
        name="Test Project"
        files={mockFiles}
        isEditable={true}
        onSave={mockOnSave}
      />
    );

    fireEvent.click(screen.getByText("root"));
    fireEvent.click(screen.getByText("file1.py"));

    expect(screen.getByText(/'hello world'/i)).toBeInTheDocument();

    const codeEditor = screen.getByTestId("code-editor");
    expect(codeEditor).toBeInTheDocument();

    expect(screen.queryByText("Save")).not.toBeInTheDocument();
    fireEvent.change(codeEditor, { target: { value: "print('hello world v2')" } });

    await waitFor(() => {
      expect(screen.getByText(/Modified/i)).toBeInTheDocument();
      expect(screen.getByTitle(/Modified/i)).toBeInTheDocument();
    });

    const saveButton = screen.getByText(/Save/i);
    expect(saveButton).toBeInTheDocument();
    expect(saveButton).toBeEnabled();
    fireEvent.click(saveButton);

    expect(mockOnSave).toHaveBeenCalled();
    await waitFor(() => {
      expect(screen.queryByText(/Modified/i)).not.toBeInTheDocument();
      expect(screen.queryByTitle(/Modified/i)).not.toBeInTheDocument();
    });
  });

  it("prompts user when trying to navigate away with unsaved changes", async () => {
    render(
      <FilesEditor
        name="Test Project"
        files={mockFiles}
        isEditable={true}
        onSave={jest.fn()}
      />
    );

    fireEvent.click(screen.getByText("root"));
    fireEvent.click(screen.getByText("file1.py"));

    const codeEditor = screen.getByTestId("code-editor");
    expect(codeEditor).toBeInTheDocument();

    fireEvent.change(codeEditor, { target: { value: "print('hello world v2')" } });

    await waitFor(() => {
      expect(screen.getByText(/Modified/i)).toBeInTheDocument();
      expect(screen.getByTitle(/Modified/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Save/i)).toBeInTheDocument();

    const mockConfirm = jest.fn().mockReturnValue(false); // User cancels navigation
    const originalConfirm = window.confirm;
    window.confirm = mockConfirm;

    await expect(mockRouter.push('/new-route')).rejects.toBe("Route change aborted");

    expect(mockConfirm).toHaveBeenCalledWith("You have unsaved changes. Leave anyway?");

    window.confirm = originalConfirm;
  });

  it("displays correct file count", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    expect(screen.getByText("2 files")).toBeInTheDocument();
  });

  it("handles nested directory structure", () => {
    render(<FilesEditor name="Test Project" files={mockFiles} />);

    fireEvent.click(screen.getByText("root"));
    expect(screen.getByText("subdirectory")).toBeInTheDocument();

    fireEvent.click(screen.getByText("subdirectory"));
    expect(screen.getByText("file2.json")).toBeInTheDocument();

    fireEvent.click(screen.getByText("file2.json"));
    expect(screen.getByText(/value/i)).toBeInTheDocument();
  });
});