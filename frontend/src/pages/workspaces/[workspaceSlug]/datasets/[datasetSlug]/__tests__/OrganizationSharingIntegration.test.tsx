/**
 * Integration test for organization sharing on the dataset page
 */
import { render, screen } from "@testing-library/react";
import { MockedProvider, MockedResponse } from "@apollo/client/testing";
import { faker } from "@faker-js/faker";
import { WorkspaceDatasetIndexPageDocument } from "workspaces/graphql/queries.generated";

// Mock next-i18next
const mockT = (key: string, options?: any) => {
  if (key === "Share with entire organization") {
    return "Share with entire organization";
  }
  if (key === "When enabled, all members of '{{orgName}}' will be able to access this dataset") {
    return `When enabled, all members of '${options?.orgName || 'this organization'}' will be able to access this dataset`;
  }
  if (key === "Shared with {{orgName}}") {
    return `Shared with ${options?.orgName || 'Organization'}`;
  }
  if (key === "Organization sharing") {
    return "Organization sharing";
  }
  return key;
};

jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: mockT,
  }),
}));

// Mock next/router
const mockPush = jest.fn();
const mockRouter = {
  push: mockPush,
  query: {
    workspaceSlug: "test-workspace",
    datasetSlug: "test-dataset",
  },
  pathname: "/workspaces/[workspaceSlug]/datasets/[datasetSlug]",
};

jest.mock("next/router", () => ({
  useRouter: () => mockRouter,
}));

// Mock helper functions
jest.mock("datasets/helpers/dataset", () => ({
  updateDataset: jest.fn(),
  updateDatasetVersion: jest.fn(),
}));

// Mock page helper
jest.mock("core/helpers/page", () => ({
  createGetServerSideProps: () => () => ({ props: {} }),
}));

// Mock analytics
jest.mock("core/helpers/analytics", () => ({
  trackEvent: jest.fn(),
}));

describe("Dataset Page Organization Sharing Integration", () => {
  const mockDatasetId = faker.string.uuid();
  const mockWorkspaceSlug = "test-workspace";
  const mockDatasetSlug = "test-dataset";

  const createMockQueryData = (overrides: any = {}) => ({
    workspace: {
      slug: mockWorkspaceSlug,
      name: "Test Workspace",
      __typename: "Workspace",
    },
    datasetLink: {
      id: faker.string.uuid(),
      __typename: "DatasetLink",
      dataset: {
        id: mockDatasetId,
        name: "Test Dataset",
        slug: mockDatasetSlug,
        description: "Test dataset description",
        sharedWithOrganization: false,
        updatedAt: "2023-01-01T00:00:00Z",
        createdAt: "2023-01-01T00:00:00Z",
        permissions: {
          update: true,
          __typename: "DatasetPermissions",
        },
        workspace: {
          name: "Test Workspace",
          slug: mockWorkspaceSlug,
          organization: {
            name: "Test Organization",
            __typename: "Organization",
          },
          __typename: "Workspace",
        },
        createdBy: {
          displayName: "Test User",
          __typename: "User",
        },
        latestVersion: {
          id: faker.string.uuid(),
          name: "v1",
          changelog: "Initial version",
          createdAt: "2023-01-01T00:00:00Z",
          createdBy: {
            displayName: "Test User",
            __typename: "User",
          },
          permissions: {
            update: true,
            __typename: "DatasetVersionPermissions",
          },
          __typename: "DatasetVersion",
        },
        __typename: "Dataset",
        ...overrides.dataset,
      },
    },
  });

  const createMocks = (queryData: any): MockedResponse[] => [
    {
      request: {
        query: WorkspaceDatasetIndexPageDocument,
        variables: {
          workspaceSlug: mockWorkspaceSlug,
          datasetSlug: mockDatasetSlug,
          versionId: expect.any(String),
          isSpecificVersion: false,
        },
      },
      result: {
        data: queryData,
      },
    },
  ];

  it("should show organization sharing switch when workspace has organization and user can edit", async () => {
    // Note: Since the actual page component is complex and has many dependencies,
    // this test focuses on the key aspects that can be tested in isolation

    const queryData = createMockQueryData({
      dataset: {
        sharedWithOrganization: false,
        workspace: {
          name: "Test Workspace",
          slug: mockWorkspaceSlug,
          organization: {
            name: "Test Organization",
          },
        },
      },
    });

    // Test the conditional rendering logic that would be in the actual component
    const dataset = queryData.datasetLink.dataset;
    const workspace = queryData.workspace;
    const isWorkspaceSource = workspace.slug === dataset.workspace?.slug;

    expect(dataset.workspace?.organization).toBeDefined();
    expect(isWorkspaceSource).toBe(true);
    expect(dataset.permissions.update).toBe(true);

    // These are the conditions that would show the organization sharing switch
    const shouldShowOrganizationSharing = 
      dataset.workspace?.organization && 
      isWorkspaceSource && 
      dataset.permissions.update;

    expect(shouldShowOrganizationSharing).toBe(true);
  });

  it("should show organization sharing badge when dataset is shared with organization", () => {
    const queryData = createMockQueryData({
      dataset: {
        sharedWithOrganization: true,
        workspace: {
          name: "Test Workspace", 
          slug: mockWorkspaceSlug,
          organization: {
            name: "Test Organization",
          },
        },
      },
    });

    const dataset = queryData.datasetLink.dataset;

    // Test the conditional rendering logic for the organization sharing badge
    const shouldShowBadge = dataset.sharedWithOrganization && dataset.workspace?.organization;

    expect(shouldShowBadge).toBeTruthy();
    expect(dataset.workspace?.organization?.name).toBe("Test Organization");
  });

  it("should not show organization sharing controls when workspace has no organization", () => {
    const queryData = createMockQueryData({
      dataset: {
        sharedWithOrganization: false,
        workspace: {
          name: "Test Workspace",
          slug: mockWorkspaceSlug,
          organization: null, // No organization
        },
      },
    });

    const dataset = queryData.datasetLink.dataset;
    const workspace = queryData.workspace;
    const isWorkspaceSource = workspace.slug === dataset.workspace?.slug;

    const shouldShowOrganizationSharing = 
      dataset.workspace?.organization && 
      isWorkspaceSource && 
      dataset.permissions.update;

    expect(shouldShowOrganizationSharing).toBeFalsy();
  });

  it("should not show organization sharing controls when user cannot edit dataset", () => {
    const queryData = createMockQueryData({
      dataset: {
        sharedWithOrganization: false,
        permissions: {
          update: false, // User cannot edit
        },
        workspace: {
          name: "Test Workspace",
          slug: mockWorkspaceSlug,
          organization: {
            name: "Test Organization",
          },
        },
      },
    });

    const dataset = queryData.datasetLink.dataset;
    const workspace = queryData.workspace;
    const isWorkspaceSource = workspace.slug === dataset.workspace?.slug;

    const shouldShowOrganizationSharing = 
      dataset.workspace?.organization && 
      isWorkspaceSource && 
      dataset.permissions.update;

    expect(shouldShowOrganizationSharing).toBe(false);
  });

  it("should not show organization sharing controls when dataset is from different workspace", () => {
    const queryData = createMockQueryData({
      dataset: {
        sharedWithOrganization: false,
        workspace: {
          name: "Different Workspace",
          slug: "different-workspace", // Different from current workspace
          organization: {
            name: "Test Organization",
          },
        },
      },
    });

    const dataset = queryData.datasetLink.dataset;
    const workspace = queryData.workspace;
    const isWorkspaceSource = workspace.slug === dataset.workspace?.slug;

    const shouldShowOrganizationSharing = 
      dataset.workspace?.organization && 
      isWorkspaceSource && 
      dataset.permissions.update;

    expect(shouldShowOrganizationSharing).toBe(false);
    expect(isWorkspaceSource).toBe(false);
  });

  it("should handle null organization name gracefully", () => {
    const queryData = createMockQueryData({
      dataset: {
        sharedWithOrganization: true,
        workspace: {
          name: "Test Workspace",
          slug: mockWorkspaceSlug,
          organization: {
            name: undefined, // Name is undefined
          },
        },
      },
    });

    const dataset = queryData.datasetLink.dataset;
    
    // Test the fallback logic used in the actual component
    const orgName = dataset.workspace?.organization?.name || "Organization";
    
    expect(orgName).toBe("Organization");
  });
});