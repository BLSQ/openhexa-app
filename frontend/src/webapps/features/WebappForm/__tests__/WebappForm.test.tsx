import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import WebappForm from "../WebappForm";
import { TestApp } from "core/helpers/testutils";
import { WebappType } from "graphql/types";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
  i18n: { t: (key: string) => key },
}));

jest.mock("next/router", () => ({
  useRouter: () => ({
    push: jest.fn(),
    pathname: "/workspaces/test-workspace/webapps/create",
  }),
}));

const mockWorkspace = {
  slug: "test-workspace",
  name: "Test Workspace",
  countries: [],
};

describe("WebappForm", () => {
  describe("Type-aware field rendering", () => {
    it("shows URL field when IFRAME type is selected", async () => {
      render(
        <TestApp>
          <WebappForm workspace={mockWorkspace} />
        </TestApp>,
      );

      await waitFor(() => {
        expect(screen.getByText("Type")).toBeInTheDocument();
      });

      const typeParent = screen.getByText("Type").closest("div") as HTMLDivElement;
      const typeCombobox = typeParent.querySelector("[role='combobox']") as HTMLElement;

      await userEvent.click(typeCombobox);

      await waitFor(() => {
        const iframeOption = screen.getByRole("option", { name: "iFrame" });
        expect(iframeOption).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole("option", { name: "iFrame" }));

      await waitFor(() => {
        expect(screen.getByText("URL")).toBeInTheDocument();
      });

      expect(screen.queryByText("Content")).not.toBeInTheDocument();
      expect(screen.queryByText("Bundle File")).not.toBeInTheDocument();
    });

    it("shows Content field with code editor when HTML type is selected", async () => {
      render(
        <TestApp>
          <WebappForm workspace={mockWorkspace} />
        </TestApp>,
      );

      await waitFor(() => {
        expect(screen.getByText("Type")).toBeInTheDocument();
      });

      const typeParent = screen.getByText("Type").closest("div") as HTMLDivElement;
      const typeCombobox = typeParent.querySelector("[role='combobox']") as HTMLElement;

      await userEvent.click(typeCombobox);

      await waitFor(() => {
        const htmlOption = screen.getByRole("option", { name: "HTML" });
        expect(htmlOption).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole("option", { name: "HTML" }));

      await waitFor(() => {
        expect(screen.getByText("Content")).toBeInTheDocument();
      });

      expect(screen.queryByText("URL")).not.toBeInTheDocument();
      expect(screen.queryByText("Bundle File")).not.toBeInTheDocument();
    });

    it("shows Bundle File field with dropzone when BUNDLE type is selected", async () => {
      render(
        <TestApp>
          <WebappForm workspace={mockWorkspace} />
        </TestApp>,
      );

      await waitFor(() => {
        expect(screen.getByText("Type")).toBeInTheDocument();
      });

      const typeParent = screen.getByText("Type").closest("div") as HTMLDivElement;
      const typeCombobox = typeParent.querySelector("[role='combobox']") as HTMLElement;

      await userEvent.click(typeCombobox);

      await waitFor(() => {
        const bundleOption = screen.getByRole("option", { name: "Bundle" });
        expect(bundleOption).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole("option", { name: "Bundle" }));

      await waitFor(() => {
        expect(screen.getByText("Bundle File")).toBeInTheDocument();
      });

      expect(screen.queryByText("URL")).not.toBeInTheDocument();
      expect(screen.queryByText("Content")).not.toBeInTheDocument();
    });

    it("shows URL field when SUPERSET type is selected", async () => {
      render(
        <TestApp>
          <WebappForm workspace={mockWorkspace} />
        </TestApp>,
      );

      await waitFor(() => {
        expect(screen.getByText("Type")).toBeInTheDocument();
      });

      const typeParent = screen.getByText("Type").closest("div") as HTMLDivElement;
      const typeCombobox = typeParent.querySelector("[role='combobox']") as HTMLElement;

      await userEvent.click(typeCombobox);

      await waitFor(() => {
        const supersetOption = screen.getByRole("option", { name: "Superset" });
        expect(supersetOption).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole("option", { name: "Superset" }));

      await waitFor(() => {
        expect(screen.getByText("URL")).toBeInTheDocument();
      });

      expect(screen.queryByText("Content")).not.toBeInTheDocument();
      expect(screen.queryByText("Bundle File")).not.toBeInTheDocument();
    });
  });

  describe("Form behavior", () => {
    it("renders with default IFRAME type", async () => {
      render(
        <TestApp>
          <WebappForm workspace={mockWorkspace} />
        </TestApp>,
      );

      await waitFor(() => {
        expect(screen.getByText("New Webapp")).toBeInTheDocument();
      });

      expect(screen.getByText("Name")).toBeInTheDocument();
      expect(screen.getByText("Type")).toBeInTheDocument();
      expect(screen.getByText("URL")).toBeInTheDocument();
    });

    it("displays webapp name when editing existing webapp", async () => {
      const mockWebapp = {
        id: "1",
        slug: "test-webapp",
        name: "Test Webapp",
        description: "",
        url: "https://example.com",
        type: WebappType.Iframe,
        icon: null,
        content: null,
        permissions: {
          update: true,
          delete: true,
        },
      };

      render(
        <TestApp>
          <WebappForm workspace={mockWorkspace} webapp={mockWebapp} />
        </TestApp>,
      );

      await waitFor(() => {
        expect(screen.getAllByText("Test Webapp").length).toBeGreaterThan(0);
      });
    });
  });
});
