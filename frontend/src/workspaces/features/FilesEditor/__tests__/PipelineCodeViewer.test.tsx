import { render, screen } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import { PipelineCodeViewer } from "../FilesEditor";

// Mock @uiw/react-codemirror
jest.mock("@uiw/react-codemirror", () => ({
  __esModule: true,
  default: ({ value }: { value: string }) => (
    <div data-testid="code-editor">{value}</div>
  ),
}));

// Mock CodeMirror language modules
jest.mock("@codemirror/lang-python", () => ({
  python: () => ({}),
}));

jest.mock("@codemirror/lang-json", () => ({
  json: () => ({}),
}));

jest.mock("@codemirror/autocomplete", () => ({
  autocompletion: () => ({}),
}));

const mockVersionData = {
  pipelineVersion: {
    id: "test-version-id",
    versionName: "v1.0",
    files: [
      {
        name: "main.py",
        path: "main.py",
        type: "file",
        content: btoa("print('Hello World')"),
      },
      {
        name: "requirements.txt",
        path: "requirements.txt",
        type: "file",
        content: btoa("pandas==1.5.0"),
      },
    ],
  },
};

const mocks = [
  {
    request: {
      query: expect.any(Object),
      variables: {
        versionId: "test-version-id",
      },
    },
    result: {
      data: mockVersionData,
    },
  },
];

describe("PipelineCodeViewer", () => {
  it("renders loading state initially", () => {
    render(
      <MockedProvider mocks={[]} addTypename={false}>
        <PipelineCodeViewer versionId="test-version-id" versionName="v1.0" />
      </MockedProvider>,
    );

    expect(screen.getByText("Loading pipeline code...")).toBeInTheDocument();
  });

  it("renders with correct props", () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <PipelineCodeViewer versionId="test-version-id" versionName="v1.0" />
      </MockedProvider>,
    );

    // Component should render without crashing
    expect(screen.getByText("Loading pipeline code...")).toBeInTheDocument();
  });
});
