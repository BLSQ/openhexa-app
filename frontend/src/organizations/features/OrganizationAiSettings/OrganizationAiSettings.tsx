import DataCard from "core/components/DataCard";
import { DescriptionListDisplayMode } from "core/components/DescriptionList";
import { OnSaveFn } from "core/components/DataCard/FormSection";
import TextProperty from "core/components/DataCard/TextProperty";
import SimpleSelectProperty from "core/components/DataCard/SimpleSelectProperty";
import SwitchProperty from "core/components/DataCard/SwitchProperty";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { AiLabel, AiModel, AiProvider } from "graphql/types";
import {
  Organization_OrganizationFragment,
  useAiLabelsQuery,
} from "organizations/graphql/queries.generated";
import { useUpdateOrganizationAiSettingsMutation } from "organizations/graphql/mutations.generated";

const MODELS: Record<string, string[]> = {
  [AiProvider.Anthropic]: ["", AiModel.Opus, AiModel.Sonnet, AiModel.Haiku],
};

type OrganizationAiSettingsProps = {
  organization: Organization_OrganizationFragment;
};

const OrganizationAiSettings = ({
  organization,
}: OrganizationAiSettingsProps) => {
  const { t } = useTranslation();
  const settings = organization.aiSettings;
  const canEdit = organization.permissions.update;

  const { data: labelsData } = useAiLabelsQuery();
  const labels = labelsData?.aiLabels;
  const isManagedInstance = Boolean(labelsData?.config?.assistantManaged);

  const [updateOrganizationAiSettings] =
    useUpdateOrganizationAiSettingsMutation();
  const [provider, setProvider] = useState<string | null | undefined>(
    settings?.provider,
  );
  const modelOptions: string[] = provider ? (MODELS[provider] ?? []) : [];

  const createLabelsMap = (
    items: AiLabel[] | null | undefined,
  ): { [k: string]: string } =>
    items != null
      ? Object.fromEntries(items.map(({ value, label }) => [value, label]))
      : {};
  const providersMap = createLabelsMap(labels?.providers);
  const modelsMap = createLabelsMap(labels?.models);
  const getProviderLabel = (type: string): string =>
    providersMap[type] || String(type);
  const getModelLabel = (type: string): string =>
    modelsMap[type] || String(type);

  const usesManagedProvider = (value: unknown) => value === AiProvider.Managed;

  const onSave: OnSaveFn = async (values) => {
    await updateOrganizationAiSettings({
      variables: {
        input: {
          organizationId: organization.id,
          enabled: values.enableAI,
          provider: isManagedInstance ? AiProvider.Managed : values.provider,
          ...(isManagedInstance
            ? {}
            : { model: values.model, apiKey: values.apiKey }),
        },
      },
    });
  };

  return (
    <DataCard item={organization} className="mt-6">
      <DataCard.FormSection
        title={t("AI assistant")}
        onSave={canEdit ? onSave : undefined}
        collapsible={false}
        displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
      >
        <SwitchProperty
          id="enableAI"
          label={t("Enabled")}
          accessor={(item) => Boolean(item?.aiSettings?.enabled)}
        />
        <SimpleSelectProperty
          id="provider"
          accessor="aiSettings.provider"
          label={t("Provider")}
          options={[AiProvider.Anthropic]}
          getOptionLabel={getProviderLabel}
          onChange={(value: string) => {
            setProvider(value);
          }}
          visible={(_, __, values) =>
            Boolean(values.enableAI) && !isManagedInstance
          }
          required={(_, __, values) =>
            Boolean(values.enableAI) && !isManagedInstance
          }
        />
        <SimpleSelectProperty
          id="model"
          accessor="aiSettings.model"
          label={t("Model")}
          options={modelOptions}
          getOptionLabel={getModelLabel}
          visible={(_, __, values) =>
            Boolean(values.enableAI) &&
            !isManagedInstance &&
            !usesManagedProvider(values.provider)
          }
          required={(_, __, values) =>
            Boolean(values.enableAI) &&
            !isManagedInstance &&
            !usesManagedProvider(values.provider)
          }
        />
        <TextProperty
          id="apiKey"
          accessor="..."
          defaultValue={settings?.hasApiKey ? "••••••" : undefined}
          placeholder={
            settings?.hasApiKey ? t("Leave blank to keep current API key") : ""
          }
          label={t("API Key")}
          visible={(_, __, values) =>
            Boolean(values.enableAI) &&
            !isManagedInstance &&
            !usesManagedProvider(values.provider)
          }
          required={(_, __, values) =>
            Boolean(values.enableAI) &&
            !isManagedInstance &&
            !usesManagedProvider(values.provider) &&
            !settings?.hasApiKey
          }
        />
      </DataCard.FormSection>
    </DataCard>
  );
};

export default OrganizationAiSettings;
