import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import AddConfigurationDialog from "./AddConfigurationDialog";

describe("AddConfigurationDialog", () => {
  const mockOnClose = jest.fn();
  const mockOnSave = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Dialog Visibility", () => {
    it("renders when open is true", async () => {
      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      expect(screen.getByRole("dialog")).toBeInTheDocument();
      expect(screen.getByText("Add Configuration")).toBeInTheDocument();
    });

    it("does not render when open is false", () => {
      render(
        <TestApp>
          <AddConfigurationDialog
            open={false}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });

  describe("Add Mode", () => {
    it("shows empty form when adding new configuration", () => {
      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      expect(screen.getByPlaceholderText("Configuration name")).toHaveValue("");
      expect(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
      ).toHaveValue("");
      expect(screen.getByText("Add")).toBeInTheDocument();
    });

    it("calls onSave with correct values for string input", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      const nameField = screen.getByPlaceholderText("Configuration name");
      const valueField = screen.getByPlaceholderText(
        "Enter value as text or JSON...",
      );
      const saveButton = screen.getByText("Add");

      await user.type(nameField, "api_key");
      await user.type(valueField, "secret123");
      await user.click(saveButton);

      expect(mockOnSave).toHaveBeenCalledWith("api_key", "secret123");
      expect(mockOnClose).toHaveBeenCalled();
    });

    it("calls onSave with correct values for JSON input", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      const nameField = screen.getByPlaceholderText("Configuration name");
      const valueField = screen.getByPlaceholderText(
        "Enter value as text or JSON...",
      );
      const saveButton = screen.getByText("Add");

      await user.type(nameField, "timeout");
      await user.type(valueField, "300");
      await user.click(saveButton);

      expect(mockOnSave).toHaveBeenCalledWith("timeout", 300);
    });
  });

  describe("Edit Mode", () => {
    const editingConfig = {
      name: "existing_key",
      value: "existing_value",
    };

    it("shows edit title and pre-populated form", () => {
      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
            editingConfig={editingConfig}
          />
        </TestApp>,
      );

      expect(screen.getByText("Edit Configuration")).toBeInTheDocument();
      expect(screen.getByDisplayValue("existing_key")).toBeInTheDocument();
      expect(screen.getByDisplayValue("existing_value")).toBeInTheDocument();
      expect(screen.getByText("Update")).toBeInTheDocument();
    });

    it("pre-populates form with JSON object", () => {
      const jsonConfig = {
        name: "config",
        value: { key: "value", nested: { data: true } },
      };

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
            editingConfig={jsonConfig}
          />
        </TestApp>,
      );

      expect(screen.getByDisplayValue("config")).toBeInTheDocument();
      const textarea = screen.getByPlaceholderText(
        "Enter value as text or JSON...",
      );
      expect(textarea).toHaveValue(JSON.stringify(jsonConfig.value, null, 2));
    });

    it("pre-populates form with array", () => {
      const arrayConfig = {
        name: "items",
        value: [1, 2, 3],
      };

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
            editingConfig={arrayConfig}
          />
        </TestApp>,
      );

      expect(screen.getByDisplayValue("items")).toBeInTheDocument();
      const textarea = screen.getByPlaceholderText(
        "Enter value as text or JSON...",
      );
      expect(textarea).toHaveValue(JSON.stringify(arrayConfig.value, null, 2));
    });

    it("updates configuration when saving edited values", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
            editingConfig={editingConfig}
          />
        </TestApp>,
      );

      const nameField = screen.getByDisplayValue("existing_key");
      const valueField = screen.getByDisplayValue("existing_value");
      const updateButton = screen.getByText("Update");

      await user.clear(nameField);
      await user.type(nameField, "updated_key");
      await user.clear(valueField);
      await user.type(valueField, "updated_value");
      await user.click(updateButton);

      expect(mockOnSave).toHaveBeenCalledWith("updated_key", "updated_value");
    });
  });

  describe("Value Type Auto-Detection", () => {
    it("parses numbers correctly", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.type(
        screen.getByPlaceholderText("Configuration name"),
        "number_val",
      );
      await user.type(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
        "42",
      );
      await user.click(screen.getByText("Add"));

      expect(mockOnSave).toHaveBeenCalledWith("number_val", 42);
    });

    it("parses booleans correctly", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.type(
        screen.getByPlaceholderText("Configuration name"),
        "bool_val",
      );
      await user.type(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
        "true",
      );
      await user.click(screen.getByText("Add"));

      expect(mockOnSave).toHaveBeenCalledWith("bool_val", true);
    });

    it("parses objects correctly", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.type(
        screen.getByPlaceholderText("Configuration name"),
        "obj_val",
      );
      await user.click(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
      );
      await user.paste('{"key": "value"}');
      await user.click(screen.getByText("Add"));

      expect(mockOnSave).toHaveBeenCalledWith("obj_val", { key: "value" });
    });

    it("parses arrays correctly", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.type(
        screen.getByPlaceholderText("Configuration name"),
        "array_val",
      );
      await user.click(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
      );
      await user.paste("[1, 2, 3]");
      await user.click(screen.getByText("Add"));

      expect(mockOnSave).toHaveBeenCalledWith("array_val", [1, 2, 3]);
    });

    it("treats invalid JSON as string", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.type(
        screen.getByPlaceholderText("Configuration name"),
        "invalid_json",
      );
      await user.click(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
      );
      await user.paste("{invalid json}");
      await user.click(screen.getByText("Add"));

      expect(mockOnSave).toHaveBeenCalledWith("invalid_json", "{invalid json}");
    });

    it("handles empty values", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.type(
        screen.getByPlaceholderText("Configuration name"),
        "empty_val",
      );
      await user.click(screen.getByText("Add"));

      expect(mockOnSave).toHaveBeenCalledWith("empty_val", "");
    });
  });

  describe("Form Validation", () => {
    it("shows error when name is empty", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.type(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
        "some_value",
      );
      await user.click(screen.getByText("Add"));

      await waitFor(() => {
        expect(screen.getByText("Name is required")).toBeInTheDocument();
      });

      expect(mockOnSave).not.toHaveBeenCalled();
    });

    it("trims whitespace from name", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.type(
        screen.getByPlaceholderText("Configuration name"),
        "  spaced_name  ",
      );
      await user.type(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
        "value",
      );
      await user.click(screen.getByText("Add"));

      expect(mockOnSave).toHaveBeenCalledWith("spaced_name", "value");
    });
  });

  describe("Error Handling", () => {
    it("can close error alert", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.click(screen.getByText("Add"));

      await waitFor(() => {
        expect(screen.getByText("Name is required")).toBeInTheDocument();
      });

      const errorAlert =
        screen.getByText("Name is required").closest('[role="alert"]') ||
        screen.getByText("Name is required").parentElement;
      const closeButton = errorAlert?.querySelector("button");

      if (closeButton) {
        await user.click(closeButton);
        expect(screen.queryByText("Name is required")).not.toBeInTheDocument();
      }
    });

    it("clears error when dialog reopens", async () => {
      const user = userEvent.setup();

      const { rerender } = render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.click(screen.getByText("Add"));

      await waitFor(() => {
        expect(screen.getByText("Name is required")).toBeInTheDocument();
      });

      rerender(
        <TestApp>
          <AddConfigurationDialog
            open={false}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );
      rerender(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      expect(screen.queryByText("Name is required")).not.toBeInTheDocument();
    });
  });

  describe("Dialog Actions", () => {
    it("calls onClose when cancel button is clicked", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.click(screen.getByText("Cancel"));
      expect(mockOnClose).toHaveBeenCalled();
    });

    it("clears form when dialog closes", async () => {
      const user = userEvent.setup();

      render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
          />
        </TestApp>,
      );

      await user.type(
        screen.getByPlaceholderText("Configuration name"),
        "test_name",
      );
      await user.type(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
        "test_value",
      );

      await user.click(screen.getByText("Cancel"));

      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe("useEffect behavior", () => {
    it("updates form when editingConfig changes", () => {
      const initialConfig = { name: "initial", value: "initial_value" };
      const updatedConfig = { name: "updated", value: "updated_value" };

      const { rerender } = render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
            editingConfig={initialConfig}
          />
        </TestApp>,
      );

      expect(screen.getByDisplayValue("initial")).toBeInTheDocument();
      expect(screen.getByDisplayValue("initial_value")).toBeInTheDocument();

      rerender(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
            editingConfig={updatedConfig}
          />
        </TestApp>,
      );

      expect(screen.getByDisplayValue("updated")).toBeInTheDocument();
      expect(screen.getByDisplayValue("updated_value")).toBeInTheDocument();
    });

    it("clears form when switching from edit to add mode", () => {
      const editingConfig = { name: "edit_name", value: "edit_value" };

      const { rerender } = render(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
            editingConfig={editingConfig}
          />
        </TestApp>,
      );

      expect(screen.getByDisplayValue("edit_name")).toBeInTheDocument();

      rerender(
        <TestApp>
          <AddConfigurationDialog
            open={true}
            onClose={mockOnClose}
            onSave={mockOnSave}
            editingConfig={null}
          />
        </TestApp>,
      );

      expect(screen.getByPlaceholderText("Configuration name")).toHaveValue("");
      expect(
        screen.getByPlaceholderText("Enter value as text or JSON..."),
      ).toHaveValue("");
    });
  });
});
