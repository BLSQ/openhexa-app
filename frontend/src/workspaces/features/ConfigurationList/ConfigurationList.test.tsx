import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import ConfigurationList from "./ConfigurationList";

jest.mock("../AddConfigurationDialog", () => {
  return function MockAddConfigurationDialog({ open, onSave, editingConfig, onClose }: any) {
    if (!open) return null;
    
    const handleSave = () => {
      if (editingConfig) {
        onSave("edited_key", "edited_value");
      } else {
        onSave("new_key", "new_value");
      }
    };

    return (
      <div data-testid="add-configuration-dialog">
        <button onClick={handleSave}>Save</button>
        <button onClick={onClose}>Close</button>
        {editingConfig && <span>Editing: {editingConfig.name}</span>}
      </div>
    );
  };
});

describe("ConfigurationList", () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Empty State", () => {
    it("displays empty state when no configurations exist", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={{}}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("No configuration properties set")).toBeInTheDocument();
      expect(screen.getByText("Click 'Add Configuration' to create your first property")).toBeInTheDocument();
    });

    it("shows add button in empty state", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={{}}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("Add Configuration")).toBeInTheDocument();
    });

    it("hides instructional text when disabled", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={{}}
            onChange={mockOnChange}
            disabled={true}
          />
        </TestApp>
      );

      expect(screen.getByText("No configuration properties set")).toBeInTheDocument();
      expect(screen.queryByText("Click 'Add Configuration' to create your first property")).not.toBeInTheDocument();
      expect(screen.queryByText("Add Configuration")).not.toBeInTheDocument();
    });
  });

  describe("Configuration Display", () => {
    const sampleConfiguration = {
      string_key: "hello world",
      number_key: 42,
      boolean_key: true,
      array_key: [1, 2, 3],
      object_key: { nested: "value" },
      null_key: null
    };

    it("displays all configuration entries", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={sampleConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("string_key")).toBeInTheDocument();
      expect(screen.getByText("number_key")).toBeInTheDocument();
      expect(screen.getByText("boolean_key")).toBeInTheDocument();
      expect(screen.getByText("array_key")).toBeInTheDocument();
      expect(screen.getByText("object_key")).toBeInTheDocument();
      expect(screen.getByText("null_key")).toBeInTheDocument();
    });

    it("displays values correctly formatted", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={sampleConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("hello world")).toBeInTheDocument();
      expect(screen.getByText("42")).toBeInTheDocument();
      expect(screen.getByText("true")).toBeInTheDocument();
      expect(screen.getByText("[1,2,3]")).toBeInTheDocument();
      expect(screen.getByText('{"nested":"value"}')).toBeInTheDocument();
      const nullElements = screen.getAllByText("null");
      expect(nullElements.length).toBeGreaterThan(0);
    });
  });

  describe("Type Badges", () => {
    const typedConfiguration = {
      text_val: "string",
      number_val: 123,
      boolean_val: false,
      array_val: ["a", "b"],
      object_val: { key: "value" },
      null_val: null
    };

    it("displays correct type badges", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={typedConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("text")).toBeInTheDocument();
      expect(screen.getByText("number")).toBeInTheDocument();
      expect(screen.getByText("boolean")).toBeInTheDocument();
      expect(screen.getByText("array")).toBeInTheDocument();
      expect(screen.getByText("object")).toBeInTheDocument();
      const nullElements = screen.getAllByText("null");
      expect(nullElements.length).toBeGreaterThan(0);
    });

    it("applies correct CSS classes for type colors", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={typedConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      const textBadge = screen.getByText("text");
      const numberBadge = screen.getByText("number");
      const booleanBadge = screen.getByText("boolean");
      const arrayBadge = screen.getByText("array");
      const objectBadge = screen.getByText("object");
      const nullElements = screen.getAllByText("null");
      const nullBadge = nullElements.find(el => el.tagName === 'SPAN')!;

      expect(textBadge).toHaveClass("bg-green-100", "text-green-800");
      expect(numberBadge).toHaveClass("bg-blue-100", "text-blue-800");
      expect(booleanBadge).toHaveClass("bg-purple-100", "text-purple-800");
      expect(arrayBadge).toHaveClass("bg-orange-100", "text-orange-800");
      expect(objectBadge).toHaveClass("bg-gray-100", "text-gray-800");
      expect(nullBadge).toHaveClass("bg-red-100", "text-red-800");
    });
  });

  describe("Add/Edit/Delete Actions", () => {
    const testConfiguration = {
      existing_key: "existing_value"
    };

    it("opens add dialog when Add Configuration is clicked", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <ConfigurationList
            configuration={testConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      await user.click(screen.getByText("Add Configuration"));
      expect(screen.getByTestId("add-configuration-dialog")).toBeInTheDocument();
    });

    it("opens edit dialog with correct data when Edit is clicked", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <ConfigurationList
            configuration={testConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      await user.click(screen.getByText("Edit"));
      
      expect(screen.getByTestId("add-configuration-dialog")).toBeInTheDocument();
      expect(screen.getByText("Editing: existing_key")).toBeInTheDocument();
    });

    it("calls onChange when adding new configuration", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <ConfigurationList
            configuration={testConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      await user.click(screen.getByText("Add Configuration"));
      await user.click(screen.getByText("Save"));

      expect(mockOnChange).toHaveBeenCalledWith({
        existing_key: "existing_value",
        new_key: "new_value"
      });
    });

    it("calls onChange when editing existing configuration", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <ConfigurationList
            configuration={testConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      await user.click(screen.getByText("Edit"));
      await user.click(screen.getByText("Save"));

      expect(mockOnChange).toHaveBeenCalledWith({
        edited_key: "edited_value"
      });
    });

    it("calls onChange when deleting configuration", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <ConfigurationList
            configuration={testConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      await user.click(screen.getByText("Delete"));

      expect(mockOnChange).toHaveBeenCalledWith({});
    });

  });

  describe("Disabled State", () => {
    const testConfiguration = {
      test_key: "test_value"
    };

    it("hides action buttons when disabled", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={testConfiguration}
            onChange={mockOnChange}
            disabled={true}
          />
        </TestApp>
      );

      expect(screen.queryByText("Add Configuration")).not.toBeInTheDocument();
      expect(screen.queryByText("Edit")).not.toBeInTheDocument();
      expect(screen.queryByText("Delete")).not.toBeInTheDocument();
    });

    it("still displays configuration data when disabled", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={testConfiguration}
            onChange={mockOnChange}
            disabled={true}
          />
        </TestApp>
      );

      expect(screen.getByText("test_key")).toBeInTheDocument();
      expect(screen.getByText("test_value")).toBeInTheDocument();
      expect(screen.getByText("text")).toBeInTheDocument(); 
    });
  });

  describe("Dialog State Management", () => {
    const testConfiguration = {
      test_key: "test_value"
    };

    it("closes dialog when onClose is called", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <ConfigurationList
            configuration={testConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      await user.click(screen.getByText("Add Configuration"));
      expect(screen.getByTestId("add-configuration-dialog")).toBeInTheDocument();

      await user.click(screen.getByText("Close"));
      expect(screen.queryByTestId("add-configuration-dialog")).not.toBeInTheDocument();
    });

    it("resets editing state when dialog closes", async () => {
      const user = userEvent.setup();
      
      render(
        <TestApp>
          <ConfigurationList
            configuration={testConfiguration}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      await user.click(screen.getByText("Edit"));
      expect(screen.getByText("Editing: test_key")).toBeInTheDocument();

      await user.click(screen.getByText("Close"));
      await user.click(screen.getByText("Add Configuration"));
      expect(screen.queryByText("Editing: test_key")).not.toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("handles undefined configuration", () => {
      render(
        <TestApp>
          <ConfigurationList
            configuration={undefined as any}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("No configuration properties set")).toBeInTheDocument();
    });

    it("handles empty string values", () => {
      const configWithEmptyString = {
        empty_string: ""
      };

      render(
        <TestApp>
          <ConfigurationList
            configuration={configWithEmptyString}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("empty_string")).toBeInTheDocument();
      const valueElements = screen.getAllByText("");
      expect(valueElements.length).toBeGreaterThan(0);
    });

    it("handles special characters in keys and values", () => {
      const specialConfig = {
        "key-with-dashes": "value with spaces",
        "key_with_underscores": "value!@#$%^&*()",
        "key.with.dots": "value/with/slashes"
      };

      render(
        <TestApp>
          <ConfigurationList
            configuration={specialConfig}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("key-with-dashes")).toBeInTheDocument();
      expect(screen.getByText("key_with_underscores")).toBeInTheDocument();
      expect(screen.getByText("key.with.dots")).toBeInTheDocument();
      expect(screen.getByText("value with spaces")).toBeInTheDocument();
      expect(screen.getByText("value!@#$%^&*()")).toBeInTheDocument();
      expect(screen.getByText("value/with/slashes")).toBeInTheDocument();
    });

    it("handles very long values", () => {
      const longValue = "a".repeat(1000);
      const configWithLongValue = {
        long_key: longValue
      };

      render(
        <TestApp>
          <ConfigurationList
            configuration={configWithLongValue}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("long_key")).toBeInTheDocument();
      expect(screen.getByText(longValue)).toBeInTheDocument();
    });

    it("handles complex nested objects", () => {
      const complexConfig = {
        complex_object: {
          level1: {
            level2: {
              level3: ["nested", "array", { deeply: "nested" }]
            }
          },
          array_with_objects: [
            { id: 1, name: "first" },
            { id: 2, name: "second" }
          ]
        }
      };

      render(
        <TestApp>
          <ConfigurationList
            configuration={complexConfig}
            onChange={mockOnChange}
          />
        </TestApp>
      );

      expect(screen.getByText("complex_object")).toBeInTheDocument();
      expect(screen.getByText("object")).toBeInTheDocument(); 
      expect(screen.getByText(JSON.stringify(complexConfig.complex_object))).toBeInTheDocument();
    });
  });
});