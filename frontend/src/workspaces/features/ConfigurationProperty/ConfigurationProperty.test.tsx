import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import DataCard from "core/components/DataCard";
import ConfigurationProperty from "./ConfigurationProperty";

jest.mock("../ConfigurationList", () => {
  return function MockConfigurationList({ configuration, onChange, disabled }: any) {
    return (
      <div data-testid="configuration-list">
        <div>Configuration count: {Object.keys(configuration || {}).length}</div>
        <div>Disabled: {disabled ? "true" : "false"}</div>
        <button 
          onClick={() => onChange({ ...configuration, new_key: "new_value" })}
          disabled={disabled}
        >
          Add Test Config
        </button>
        {Object.entries(configuration || {}).map(([key, value]) => (
          <div key={key}>
            {key}: {typeof value === "string" ? value : JSON.stringify(value)}
          </div>
        ))}
      </div>
    );
  };
});

describe("ConfigurationProperty", () => {
  const mockWorkspace = {
    configuration: {
      existing_key: "existing_value",
      number_key: 42,
      object_key: { nested: "data" }
    }
  };

  describe("DataCard Integration", () => {
    it("renders within DataCard context", () => {
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByTestId("configuration-list")).toBeInTheDocument();
      expect(screen.getByText("Configuration count: 3")).toBeInTheDocument();
    });

    it("displays configuration data correctly", () => {
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByText("existing_key: existing_value")).toBeInTheDocument();
      expect(screen.getByText("number_key: 42")).toBeInTheDocument();
      expect(screen.getByText('object_key: {"nested":"data"}')).toBeInTheDocument();
    });

    it("handles empty configuration", () => {
      const emptyWorkspace = { configuration: {} };
      
      render(
        <TestApp>
          <DataCard item={emptyWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByText("Configuration count: 0")).toBeInTheDocument();
    });

    it("handles undefined configuration with defaultValue", () => {
      const workspaceWithoutConfig = {};
      const defaultConfig = { default_key: "default_value" } as any;
      
      render(
        <TestApp>
          <DataCard item={workspaceWithoutConfig}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
                defaultValue={defaultConfig}
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByText("Configuration count: 1")).toBeInTheDocument();
      expect(screen.getByText("default_key: default_value")).toBeInTheDocument();
    });
  });

  describe("Edit/Display Modes", () => {
    it("shows editable interface in edit mode", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      const editButton = screen.getByText("Edit");
      await user.click(editButton);

      expect(screen.getByTestId("configuration-list")).toBeInTheDocument();
      expect(screen.getByText("Disabled: false")).toBeInTheDocument();
      expect(screen.getByText("Add Test Config")).toBeEnabled();
    });

    it("shows read-only interface in display mode", () => {
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByTestId("configuration-list")).toBeInTheDocument();
      expect(screen.getByText("Disabled: true")).toBeInTheDocument();
      expect(screen.getByText("Add Test Config")).toBeDisabled();
    });

    it("uses formValue in edit mode", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      await user.click(screen.getByText("Edit"));

      expect(screen.getByText("Configuration count: 3")).toBeInTheDocument();
    });

    it("uses displayValue in display mode", () => {
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByText("Configuration count: 3")).toBeInTheDocument();
    });
  });

  describe("Value Handling", () => {
    it("renders ConfigurationList with correct props", () => {
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByTestId("configuration-list")).toBeInTheDocument();
      expect(screen.getByText("Configuration count: 3")).toBeInTheDocument();
      expect(screen.getByText("existing_key: existing_value")).toBeInTheDocument();
      expect(screen.getByText("number_key: 42")).toBeInTheDocument();
      expect(screen.getByText('object_key: {"nested":"data"}')).toBeInTheDocument();
    });

    it("handles readonly property", () => {
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
                readonly={true}
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByText("Disabled: true")).toBeInTheDocument();
    });

    it("handles invisible property", () => {
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
                visible={false}
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.queryByTestId("configuration-list")).not.toBeInTheDocument();
    });

    it("handles conditional visibility", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
                visible={(value, isEditing) => isEditing || Object.keys(value || {}).length > 0}
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByTestId("configuration-list")).toBeInTheDocument();

      await user.click(screen.getByText("Edit"));
      expect(screen.getByTestId("configuration-list")).toBeInTheDocument();
    });

    it("hides when conditional visibility returns false", () => {
      const emptyWorkspace = { configuration: {} };
      
      render(
        <TestApp>
          <DataCard item={emptyWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
                visible={(value, isEditing) => !isEditing && Object.keys(value || {}).length > 0}
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      // Should not be visible because configuration is empty and we're not editing
      expect(screen.queryByTestId("configuration-list")).not.toBeInTheDocument();
    });
  });

  describe("Default Value Handling", () => {
    it("uses defaultValue when configuration is undefined", () => {
      const workspaceWithoutConfig = {};
      const defaultConfig = { 
        default_key: "default_value",
        default_number: 123
      } as any;
      
      render(
        <TestApp>
          <DataCard item={workspaceWithoutConfig}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
                defaultValue={defaultConfig}
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByText("Configuration count: 2")).toBeInTheDocument();
      expect(screen.getByText("default_key: default_value")).toBeInTheDocument();
      expect(screen.getByText("default_number: 123")).toBeInTheDocument();
    });

    it("uses actual value when configuration exists, ignoring defaultValue", () => {
      const defaultConfig = { default_key: "default_value" } as any;
      
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
                defaultValue={defaultConfig}
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByText("Configuration count: 3")).toBeInTheDocument();
      expect(screen.getByText("existing_key: existing_value")).toBeInTheDocument();
      expect(screen.queryByText("default_key: default_value")).not.toBeInTheDocument();
    });

    it("uses empty object as default when no defaultValue provided", () => {
      const workspaceWithoutConfig = {};
      
      render(
        <TestApp>
          <DataCard item={workspaceWithoutConfig}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByText("Configuration count: 0")).toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("handles null configuration", () => {
      const workspaceWithNullConfig = { configuration: null };
      
      render(
        <TestApp>
          <DataCard item={workspaceWithNullConfig}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByText("Configuration count: 0")).toBeInTheDocument();
    });

    it("handles non-object configuration gracefully", () => {
      const workspaceWithStringConfig = { configuration: "not an object" as any };
      
      render(
        <TestApp>
          <DataCard item={workspaceWithStringConfig}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Configuration"
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByTestId("configuration-list")).toBeInTheDocument();
    });
  });

  describe("Property Definition Props", () => {
    it("passes through standard PropertyDefinition props", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <DataCard item={mockWorkspace}>
            <DataCard.FormSection title="Test Section" onSave={async () => {}}>
              <ConfigurationProperty
                id="configuration"
                accessor="configuration"
                label="Test Configuration Label"
                help="This is configuration help text"
                required={true}
              />
            </DataCard.FormSection>
          </DataCard>
        </TestApp>
      );

      expect(screen.getByTestId("configuration-list")).toBeInTheDocument();
      
      await user.click(screen.getByText("Edit"));
      expect(screen.getByTestId("configuration-list")).toBeInTheDocument();
    });
  });
});