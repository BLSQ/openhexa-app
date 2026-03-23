import DataCard from "core/components/DataCard";
import { DescriptionListDisplayMode } from "core/components/DescriptionList";
import { OnSaveFn } from "core/components/DataCard/FormSection";
import TextProperty from "core/components/DataCard/TextProperty";
import { useUpdateUserAiSettingsMutation } from "identity/graphql/mutations.generated";
import SimpleSelectProperty from "core/components/DataCard/SimpleSelectProperty";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import {
  AiLabel,
  AiLabels,
  AiModel,
  AiProvider,
  AiSettings,
  Maybe,
  User,
} from "graphql/types";
import SwitchProperty from "core/components/DataCard/SwitchProperty";

const MODELS: Record<string, string[]> = {
  anthropic: ["", AiModel.Opus, AiModel.Sonnet, AiModel.Haiku],
};

type AccountAiSettingsProps = {
  settings?: Maybe<AiSettings>;
  labels: Maybe<AiLabels>;
  monthlyCost: number;
  totalCost: number;
  refetch: any;
};

const AccountAiSettings = (props: AccountAiSettingsProps) => {
  const { settings, labels, monthlyCost, totalCost, refetch } = props;
  const [updateUserAiSettings] = useUpdateUserAiSettingsMutation();
  const [provider, setProvider] = useState<string | null | undefined>(settings?.provider);
  const modelOptions: string[] = provider ? (MODELS[provider] ?? []) : [];

  const createLabelsMap = (labels: Maybe<AiLabel[]> | undefined): {[k:string]: string} => {
    if (labels != null) {
      return Object.fromEntries(
        labels.map(({ value, label }: AiLabel) => [value, label])
      )
    } else {
      return {}
    }
  };
  const providersMap = createLabelsMap(labels?.providers)
  const modelsMap = createLabelsMap(labels?.models);
  const getProviderLabel = (type: AiProvider | string): string => providersMap[type] || String(type);
  const getModelLabel = (type: AiModel | string): string => modelsMap[type] || String(type);

  const { t } = useTranslation();

  const onSave: OnSaveFn = async (values, item) => {
    await updateUserAiSettings({
      variables: {
        input: {
          enabled: values.enableAI,
          provider: values.provider,
          model: values.model,
          apiKey: values.apiKey,
        },
      },
    });
    await refetch();
  };

  return (
    <DataCard.FormSection
      title={t("AI Agents")}
      onSave={onSave}
      collapsible={false}
      displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
    >
      <SwitchProperty
        id="enableAI"
        label={t("Enabled")}
        accessor={(item: User) => {
          return Boolean(item?.aiSettings?.enabled);
        }}
      />
      <SimpleSelectProperty
        id="provider"
        accessor="aiSettings.provider"
        label={t("Provider")}
        options={[AiProvider.Anthropic]}
        getOptionLabel={getProviderLabel}
        onChange={(value: string) => { setProvider(value); }}
        visible={(_, __, values) =>
          Boolean(values.enableAI)
        }
        required={(_, __, values) => Boolean(values.enableAI)}
      />
      <SimpleSelectProperty
        id="model"
        accessor="aiSettings.model"
        label={t("Model")}
        options={modelOptions}
        getOptionLabel={getModelLabel}
        visible={(_, __, values) =>
          Boolean(values.enableAI)
        }
        required={(_, __, values) => Boolean(values.enableAI) && provider !== null}
      />
      <TextProperty
        id="apiKey"
        accessor="..."
        defaultValue={settings?.hasApiKey ? "••••••" : undefined}
        placeholder={settings?.hasApiKey ? t("Leave blank to keep current API key") : ""}
        label={t("API Key")}
        visible={(_, __, values) =>
          Boolean(values.enableAI)
        }
        required={!settings?.hasApiKey}
      />
      <TextProperty
        id="totalCost"
        label={t("Total cost")}
        accessor={() => `$${totalCost.toFixed(4)}`}
        readonly
        visible={(_, __, values) => Boolean(values.enableAI)}
      />
      <TextProperty
        id="monthlyCost"
        label={t("Current month cost")}
        accessor={() => `$${monthlyCost.toFixed(4)}`}
        readonly
        visible={(_, __, values) => Boolean(values.enableAI)}
      />
    </DataCard.FormSection>
  );
};

export default AccountAiSettings;
