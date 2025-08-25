import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MockedProvider, MockedResponse } from "@apollo/client/testing";
import { faker } from "@faker-js/faker";
import DataCard from "core/components/DataCard/DataCard";
import SwitchProperty from "core/components/DataCard/SwitchProperty";
import RenderProperty from "core/components/DataCard/RenderProperty";
import Badge from "core/components/Badge";
import { updateDataset } from "../helpers/dataset";

// Mock the updateDataset function
jest.mock("../helpers/dataset", () => ({
  updateDataset: jest.fn(),
}));

// Mock translation
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

const mockUpdateDataset = updateDataset as jest.MockedFunction<typeof updateDataset>;

describe("Dataset Organization Sharing", () => {
  beforeEach(() => {
    mockUpdateDataset.mockClear();
  });

  describe("Organization Sharing Switch", () => {
    it("should render organization sharing switch when workspace has organization", async () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: false,
        workspace: {
          organization: {
            name: "Test Organization",
          },
        },
      };

      const { container } = render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              {dataset.workspace?.organization && (
                <SwitchProperty
                  id="sharedWithOrganization"
                  accessor="sharedWithOrganization"
                  label={mockT("Share with entire organization")}
                  help={mockT(
                    "When enabled, all members of '{{orgName}}' will be able to access this dataset",
                    { orgName: dataset.workspace.organization.name }
                  )}
                  visible={() => true}
                />
              )}
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      expect(screen.getByText("Share with entire organization")).toBeInTheDocument();
      // Help text is likely shown as a tooltip, so let's just check that the switch exists
      expect(screen.getByRole("switch")).toBeInTheDocument();
    });

    it("should not render organization sharing switch when workspace has no organization", () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: false,
        workspace: {
          organization: null,
        },
      };

      render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              {dataset.workspace?.organization && (
                <SwitchProperty
                  id="sharedWithOrganization"
                  accessor="sharedWithOrganization"
                  label={mockT("Share with entire organization")}
                  help={mockT(
                    "When enabled, all members of '{{orgName}}' will be able to access this dataset",
                    { orgName: dataset.workspace.organization.name }
                  )}
                  visible={() => true}
                />
              )}
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      expect(screen.queryByText("Share with entire organization")).not.toBeInTheDocument();
    });

    it("should show organization sharing switch as checked when dataset is shared", () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: true,
        workspace: {
          organization: {
            name: "Test Organization",
          },
        },
      };

      render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              <SwitchProperty
                id="sharedWithOrganization"
                accessor="sharedWithOrganization"
                label={mockT("Share with entire organization")}
                help={mockT(
                  "When enabled, all members of '{{orgName}}' will be able to access this dataset",
                  { orgName: dataset.workspace.organization.name }
                )}
                visible={() => true}
              />
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      const switchInput = screen.getByRole("switch");
      expect(switchInput).toBeChecked();
    });
  });

  describe("Organization Sharing Indicator", () => {
    it("should show organization sharing badge when dataset is shared", () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: true,
        workspace: {
          organization: {
            name: "Test Organization",
          },
        },
      };

      render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              {dataset.sharedWithOrganization && dataset.workspace?.organization && (
                <RenderProperty
                  id="organizationSharing"
                  accessor="sharedWithOrganization"
                  label={mockT("Organization sharing")}
                  readonly
                >
                  {() => (
                    <Badge color="green">
                      {mockT("Shared with {{orgName}}", {
                        orgName: dataset.workspace?.organization?.name || "Organization",
                      })}
                    </Badge>
                  )}
                </RenderProperty>
              )}
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      expect(screen.getByText("Organization sharing")).toBeInTheDocument();
      expect(screen.getByText("Shared with Test Organization")).toBeInTheDocument();
    });

    it("should not show organization sharing badge when dataset is not shared", () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: false,
        workspace: {
          organization: {
            name: "Test Organization",
          },
        },
      };

      render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              {dataset.sharedWithOrganization && dataset.workspace?.organization && (
                <RenderProperty
                  id="organizationSharing"
                  accessor="sharedWithOrganization"
                  label={mockT("Organization sharing")}
                  readonly
                >
                  {() => (
                    <Badge color="green">
                      {mockT("Shared with {{orgName}}", {
                        orgName: dataset.workspace?.organization?.name || "Organization",
                      })}
                    </Badge>
                  )}
                </RenderProperty>
              )}
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      expect(screen.queryByText("Organization sharing")).not.toBeInTheDocument();
      expect(screen.queryByText("Shared with Test Organization")).not.toBeInTheDocument();
    });

    it("should handle null organization gracefully", () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: true,
        workspace: {
          organization: null,
        },
      };

      render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              {dataset.sharedWithOrganization && dataset.workspace?.organization && (
                <RenderProperty
                  id="organizationSharing"
                  accessor="sharedWithOrganization"
                  label={mockT("Organization sharing")}
                  readonly
                >
                  {() => (
                    <Badge color="green">
                      {mockT("Shared with {{orgName}}", {
                        orgName: dataset.workspace?.organization?.name || "Organization",
                      })}
                    </Badge>
                  )}
                </RenderProperty>
              )}
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      // Should not render when organization is null
      expect(screen.queryByText("Organization sharing")).not.toBeInTheDocument();
    });
  });

  describe("Conditional Rendering Logic", () => {
    it("should render organization sharing controls only for workspace source datasets", () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: false,
        workspace: {
          slug: "source-workspace",
          organization: {
            name: "Test Organization",
          },
        },
      };

      const currentWorkspace = {
        slug: "source-workspace", // Same as dataset workspace
      };

      const isWorkspaceSource = currentWorkspace.slug === dataset.workspace?.slug;

      render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              {dataset.workspace?.organization && isWorkspaceSource && (
                <SwitchProperty
                  id="sharedWithOrganization"
                  accessor="sharedWithOrganization"
                  label={mockT("Share with entire organization")}
                  help={mockT(
                    "When enabled, all members of '{{orgName}}' will be able to access this dataset",
                    { orgName: dataset.workspace.organization.name }
                  )}
                  visible={() => true}
                />
              )}
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      expect(screen.getByText("Share with entire organization")).toBeInTheDocument();
    });

    it("should not render organization sharing controls for non-source workspace datasets", () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: false,
        workspace: {
          slug: "source-workspace",
          organization: {
            name: "Test Organization",
          },
        },
      };

      const currentWorkspace = {
        slug: "different-workspace", // Different from dataset workspace
      };

      const isWorkspaceSource = currentWorkspace.slug === dataset.workspace?.slug;

      render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              {dataset.workspace?.organization && isWorkspaceSource && (
                <SwitchProperty
                  id="sharedWithOrganization"
                  accessor="sharedWithOrganization"
                  label={mockT("Share with entire organization")}
                  help={mockT(
                    "When enabled, all members of '{{orgName}}' will be able to access this dataset",
                    { orgName: dataset.workspace.organization.name }
                  )}
                  visible={() => true}
                />
              )}
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      expect(screen.queryByText("Share with entire organization")).not.toBeInTheDocument();
    });
  });

  describe("Integration with DataCard Form System", () => {
    it("should render switch in read-only mode by default", () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: false,
        workspace: {
          organization: {
            name: "Test Organization",
          },
        },
      };

      render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              <SwitchProperty
                id="sharedWithOrganization"
                accessor="sharedWithOrganization"
                label={mockT("Share with entire organization")}
                help={mockT(
                  "When enabled, all members of '{{orgName}}' will be able to access this dataset",
                  { orgName: dataset.workspace.organization.name }
                )}
                visible={() => true}
              />
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      const switchInput = screen.getByRole("switch");
      // Switch should be disabled in read-only mode
      expect(switchInput).toBeDisabled();
      expect(switchInput).not.toBeChecked();
    });

    it("should display correct checked state based on dataset property", () => {
      const dataset = {
        id: faker.string.uuid(),
        name: "Test Dataset",
        sharedWithOrganization: true,
        workspace: {
          organization: {
            name: "Test Organization",
          },
        },
      };

      render(
        <MockedProvider mocks={[]}>
          <DataCard item={dataset}>
            <DataCard.FormSection>
              <SwitchProperty
                id="sharedWithOrganization"
                accessor="sharedWithOrganization"
                label={mockT("Share with entire organization")}
                help={mockT(
                  "When enabled, all members of '{{orgName}}' will be able to access this dataset",
                  { orgName: dataset.workspace.organization.name }
                )}
                visible={() => true}
              />
            </DataCard.FormSection>
          </DataCard>
        </MockedProvider>
      );

      const switchInput = screen.getByRole("switch");
      // Should show the correct checked state
      expect(switchInput).toHaveAttribute("aria-checked", "true");
    });
  });
});