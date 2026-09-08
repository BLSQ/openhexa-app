import { render, screen, waitFor } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { FileType, PipelineType } from "graphql/types";
import mockRouter from "next-router-mock";
import PipelineDetail from "pipelines/features/PipelineDetail/PipelineDetail";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
  // workspaces/helpers/pipelines formats labels through the i18n singleton
  i18n: { t: (key: string) => key },
  Trans: ({ children }: any) => children,
}));

jest.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (str: string) => str,
    i18n: { changeLanguage: jest.fn() },
  }),
  Trans: ({ children }: any) => children,
}));

jest.mock("core/components/CodeMirrorClient/CodeMirrorClient", () => {
  return function MockCodeMirror({ value, onChange, readOnly }: any) {
    return (
      <textarea
        data-testid="code-editor"
        value={value}
        onChange={(e) => onChange && onChange(e.target.value)}
        readOnly={readOnly}
      />
    );
  };
});

jest.mock("assistant/features/PipelineEditChatPanel", () => ({
  __esModule: true,
  default: () => <div data-testid="pipeline-edit-chat-panel" />,
}));

const WORKSPACE_SLUG = "test-workspace";
const PIPELINE_CODE = "simple-etl";

const buildPipeline = (createVersion: boolean) => ({
  __typename: "Pipeline",
  id: "pipeline-1",
  code: PIPELINE_CODE,
  name: "Simple ETL",
  description: null,
  type: PipelineType.ZipFile,
  functionalType: null,
  notebookPath: null,
  schedule: null,
  webhookEnabled: false,
  webhookUrl: null,
  autoUpdateFromTemplate: false,
  hasNewTemplateVersions: false,
  permissions: {
    createVersion,
    run: false,
    delete: false,
    update: createVersion,
    schedule: false,
    createTemplateVersion: { isAllowed: false, reasons: [] },
  },
  tags: [],
  template: null,
  sourceTemplate: null,
  newTemplateVersions: [],
  scheduledPipelineVersion: null,
  versions: { items: [] },
  currentVersion: {
    __typename: "PipelineVersion",
    id: "version-1",
    versionName: "v1",
    name: "v1",
    description: null,
    config: {},
    externalLink: null,
    createdAt: "2024-12-17T09:46:09.856Z",
    templateVersion: null,
    user: { displayName: "root@openhexa.org" },
    parameters: [],
    files: [
      {
        __typename: "FileNode",
        id: "file-1",
        name: "pipeline.py",
        path: "/pipeline.py",
        type: FileType.File,
        content: "print('hello world')",
        encoding: null,
        parentId: null,
        autoSelect: true,
        language: "python",
        lineCount: 1,
      },
    ],
  },
  assistantConversations: [
    {
      id: "conversation-1",
      name: "First conversation",
      createdAt: "2024-12-17T09:46:09.856Z",
      updatedAt: "2024-12-17T09:46:09.856Z",
    },
  ],
});

const renderCodeTab = (createVersion: boolean) => {
  mockRouter.setCurrentUrl(
    `/workspaces/${WORKSPACE_SLUG}/pipelines/${PIPELINE_CODE}?tab=code`,
  );
  return render(
    <TestApp>
      <PipelineDetail
        workspaceSlug={WORKSPACE_SLUG}
        pipelineCode={PIPELINE_CODE}
        pipeline={buildPipeline(createVersion)}
        showAssistant
        aiBudgetLimitReached={false}
        monthlyLimitExceeded={false}
        onRefetch={jest.fn()}
      />
    </TestApp>,
  );
};

describe("PipelineDetail code view", () => {
  it("shows a read-only editor without AI assistant when the user cannot create versions", async () => {
    renderCodeTab(false);

    const editor = await screen.findByTestId("code-editor");
    expect(editor).toHaveAttribute("readonly");
    expect(
      screen.queryByRole("button", { name: "AI Assistant" }),
    ).not.toBeInTheDocument();
    // Even with existing conversations, the chat panel must not open for viewers
    expect(
      screen.queryByTestId("pipeline-edit-chat-panel"),
    ).not.toBeInTheDocument();
  });

  it("shows an editable editor with the AI assistant when the user can create versions", async () => {
    renderCodeTab(true);

    const editor = await screen.findByTestId("code-editor");
    expect(editor).not.toHaveAttribute("readonly");
    await waitFor(() => {
      expect(
        screen.getByTestId("pipeline-edit-chat-panel"),
      ).toBeInTheDocument();
    });
  });
});
