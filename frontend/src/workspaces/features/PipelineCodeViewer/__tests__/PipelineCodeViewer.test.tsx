import { render, screen } from "@testing-library/react";
import { PipelineCodeViewer } from "../PipelineCodeViewer";

// Mock JSZip
jest.mock("jszip", () => {
  return jest.fn().mockImplementation(() => ({
    loadAsync: jest.fn().mockResolvedValue(undefined),
    forEach: jest.fn(),
  }));
});

// Mock @codeium/react-code-editor
jest.mock("@codeium/react-code-editor", () => ({
  CodeiumEditor: ({ value }: { value: string }) => <div data-testid="code-editor">{value}</div>,
}));

// Mock next/dynamic
jest.mock("next/dynamic", () => () => {
  const MockedCodeiumEditor = ({ value }: { value: string }) => <div data-testid="code-editor">{value}</div>;
  return MockedCodeiumEditor;
});

describe("PipelineCodeViewer", () => {
  it("renders loading state initially", () => {
    render(<PipelineCodeViewer zipfile="dGVzdA==" versionName="v1.0" />);
    
    expect(screen.getByText("Extracting pipeline code...")).toBeInTheDocument();
  });

  it("renders with correct props", () => {
    render(<PipelineCodeViewer zipfile="dGVzdA==" versionName="v1.0" />);
    
    // Component should render without crashing
    expect(screen.getByText("Extracting pipeline code...")).toBeInTheDocument();
  });
});