import { render, screen, waitFor } from "@testing-library/react";
import { MockedResponse } from "@apollo/client/testing";
import { FileType, PipelineType } from "graphql/types";
import WorkspacePipelineCodePage from "pages/workspaces/[workspaceSlug]/pipelines/[pipelineCode]/code";
import { TestApp } from "core/helpers/testutils";
import { SidebarMenuDocument } from "workspaces/features/SidebarMenu/SidebarMenu.generated";
import { WorkspacePipelineCodePageDocument } from "workspaces/graphql/queries.generated";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
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

const mockWorkspace = {
  __typename: "Workspace",
  slug: WORKSPACE_SLUG,
  name: "Test Workspace",
  webappsEnabled: false,
  organization: {
    id: "org-1",
    name: "Test Organization",
    shortName: "Test Org",
    logo: null,
    aiSettings: { enabled: true },
    aiBudgetLimitReached: false,
    permissions: {
      createWorkspace: { isAllowed: false, reasons: [] },
    },
  },
  permissions: {
    manageMembers: false,
    update: false,
    launchNotebookServer: false,
  },
  shortcuts: [],
  countries: [],
};

const sidebarMenuMock: MockedResponse = {
  request: {
    query: SidebarMenuDocument,
    variables: {
      page: 1,
      perPage: 2000,
      organizationId: "org-1",
    },
  },
  maxUsageCount: Infinity,
  result: {
    data: {
      pendingWorkspaceInvitations: { totalItems: 0 },
      workspaces: {
        totalItems: 1,
        items: [
          {
            slug: WORKSPACE_SLUG,
            name: "Test Workspace",
            countries: [],
          },
        ],
      },
    },
  },
};

const codePageMock = (createVersion: boolean): MockedResponse => ({
  request: {
    query: WorkspacePipelineCodePageDocument,
    variables: {
      workspaceSlug: WORKSPACE_SLUG,
      pipelineCode: PIPELINE_CODE,
    },
  },
  result: {
    data: {
      workspace: mockWorkspace,
      pipeline: {
        __typename: "Pipeline",
        id: "pipeline-1",
        code: PIPELINE_CODE,
        name: "Simple ETL",
        type: PipelineType.ZipFile,
        permissions: {
          createVersion,
          run: false,
          delete: false,
          update: createVersion,
          createTemplateVersion: { isAllowed: false, reasons: [] },
        },
        template: null,
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
          pipeline: {
            id: "pipeline-1",
            code: PIPELINE_CODE,
            workspace: { slug: WORKSPACE_SLUG },
          },
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
        workspace: { slug: WORKSPACE_SLUG },
      },
      me: { assistantMonthlyLimitExceeded: false },
    },
  },
});

describe("WorkspacePipelineCodePage", () => {
  it("shows a read-only editor without AI assistant when the user cannot create versions", async () => {
    render(
      <TestApp mocks={[sidebarMenuMock, codePageMock(false)]}>
        <WorkspacePipelineCodePage
          workspaceSlug={WORKSPACE_SLUG}
          pipelineCode={PIPELINE_CODE}
        />
      </TestApp>,
    );

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

  it("shows an editable editor with AI assistant when the user can create versions", async () => {
    render(
      <TestApp mocks={[sidebarMenuMock, codePageMock(true)]}>
        <WorkspacePipelineCodePage
          workspaceSlug={WORKSPACE_SLUG}
          pipelineCode={PIPELINE_CODE}
        />
      </TestApp>,
    );

    const editor = await screen.findByTestId("code-editor");
    expect(editor).not.toHaveAttribute("readonly");
    expect(
      screen.getByRole("button", { name: "AI Assistant" }),
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(
        screen.getByTestId("pipeline-edit-chat-panel"),
      ).toBeInTheDocument();
    });
  });
});
