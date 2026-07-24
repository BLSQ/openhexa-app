import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { v4 } from "uuid";
import { TestApp } from "core/helpers/testutils";
import { AiProvider } from "graphql/types";
import { useAiLabelsQuery } from "organizations/graphql/queries.generated";
import { useUpdateOrganizationAiSettingsMutation } from "organizations/graphql/mutations.generated";
import OrganizationAiSettings from "../OrganizationAiSettings";

jest.mock("organizations/graphql/queries.generated", () => ({
  ...jest.requireActual("organizations/graphql/queries.generated"),
  useAiLabelsQuery: jest.fn(),
}));

jest.mock("organizations/graphql/mutations.generated", () => ({
  ...jest.requireActual("organizations/graphql/mutations.generated"),
  useUpdateOrganizationAiSettingsMutation: jest.fn(),
}));

jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
  Trans: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  i18n: {
    t: (key: string) => key,
  },
}));

const useAiLabelsQueryMock = useAiLabelsQuery as jest.Mock;
const useUpdateOrganizationAiSettingsMutationMock =
  useUpdateOrganizationAiSettingsMutation as jest.Mock;

const AI_LABELS = {
  providers: [
    { value: "managed", label: "Managed" },
    { value: "anthropic", label: "Anthropic" },
  ],
  models: [
    { value: "opus", label: "Opus" },
    { value: "sonnet", label: "Sonnet" },
    { value: "haiku", label: "Haiku" },
  ],
};

const buildOrganization = (aiSettings: {
  enabled: boolean;
  provider: AiProvider | null;
  model?: string | null;
  hasApiKey?: boolean;
}) =>
  ({
    id: v4(),
    permissions: { update: true },
    aiSettings: {
      model: null,
      hasApiKey: false,
      ...aiSettings,
    },
  }) as any;

const mockAiLabels = (assistantManaged: boolean) => {
  useAiLabelsQueryMock.mockReturnValue({
    data: {
      aiLabels: AI_LABELS,
      config: { assistantManaged },
    },
  });
};

const getProviderSelect = () => {
  const selects = screen.getAllByRole("combobox");
  const providerSelect = selects.find((select) =>
    within(select).queryByRole("option", { name: "Anthropic" }),
  );
  if (!providerSelect) {
    throw new Error("Provider select not found");
  }
  return providerSelect;
};

const getOptionLabels = (select: HTMLElement) =>
  within(select)
    .getAllByRole("option")
    .map((option) => option.textContent);

describe("OrganizationAiSettings", () => {
  beforeEach(() => {
    useAiLabelsQueryMock.mockReset();
    useUpdateOrganizationAiSettingsMutationMock.mockReset();
    useUpdateOrganizationAiSettingsMutationMock.mockReturnValue([
      jest.fn().mockResolvedValue({}),
      {},
    ]);
  });

  it("offers both Managed and Anthropic providers on a managed instance", async () => {
    mockAiLabels(true);
    const user = userEvent.setup();

    render(
      <TestApp>
        <OrganizationAiSettings
          organization={buildOrganization({
            enabled: true,
            provider: AiProvider.Managed,
          })}
        />
      </TestApp>,
    );

    await user.click(screen.getByRole("button", { name: "Edit" }));

    expect(getOptionLabels(getProviderSelect())).toEqual([
      "Managed",
      "Anthropic",
    ]);

    // Managed provider keeps the BYOK fields hidden.
    expect(screen.queryByText("Model")).not.toBeInTheDocument();
    expect(screen.queryByText("API Key")).not.toBeInTheDocument();
  });

  it("reveals the model and API key fields when switching to Anthropic on a managed instance", async () => {
    mockAiLabels(true);
    const user = userEvent.setup();

    render(
      <TestApp>
        <OrganizationAiSettings
          organization={buildOrganization({
            enabled: true,
            provider: AiProvider.Managed,
          })}
        />
      </TestApp>,
    );

    await user.click(screen.getByRole("button", { name: "Edit" }));
    await user.selectOptions(getProviderSelect(), "anthropic");

    await waitFor(() => {
      expect(screen.getByText("Model")).toBeInTheDocument();
      expect(screen.getByText("API Key")).toBeInTheDocument();
    });
  });

  it("does not resend the masked API key when it is left untouched", async () => {
    mockAiLabels(false);
    const mutate = jest.fn().mockResolvedValue({});
    useUpdateOrganizationAiSettingsMutationMock.mockReturnValue([mutate, {}]);
    const user = userEvent.setup();

    render(
      <TestApp>
        <OrganizationAiSettings
          organization={buildOrganization({
            enabled: true,
            provider: AiProvider.Anthropic,
            model: "opus",
            hasApiKey: true,
          })}
        />
      </TestApp>,
    );

    await user.click(screen.getByRole("button", { name: "Edit" }));
    await user.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(mutate).toHaveBeenCalled());

    const { apiKey } = mutate.mock.calls[0][0].variables.input;
    expect(apiKey).not.toBe("••••••");
  });

  it("only offers the Anthropic provider on a self-hosted instance", async () => {
    mockAiLabels(false);
    const user = userEvent.setup();

    render(
      <TestApp>
        <OrganizationAiSettings
          organization={buildOrganization({
            enabled: true,
            provider: AiProvider.Anthropic,
          })}
        />
      </TestApp>,
    );

    await user.click(screen.getByRole("button", { name: "Edit" }));

    expect(getOptionLabels(getProviderSelect())).toEqual(["Anthropic"]);

    // Anthropic provider always exposes the BYOK fields.
    expect(screen.getByText("Model")).toBeInTheDocument();
    expect(screen.getByText("API Key")).toBeInTheDocument();
  });
});
