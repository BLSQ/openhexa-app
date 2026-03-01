import DataCard from "core/components/DataCard";
import { DescriptionListDisplayMode } from "core/components/DescriptionList";
import { OnSaveFn } from "core/components/DataCard/FormSection";
import TextProperty from "core/components/DataCard/TextProperty";
import { useUpdateUserAiSettingsMutation } from "identity/graphql/mutations.generated";
import SimpleSelectProperty from "core/components/DataCard/SimpleSelectProperty";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { AiModel, AiProvider, AiSettings, User } from "graphql/types";
import SwitchProperty from "core/components/DataCard/SwitchProperty";

const MODELS: Record<string, AiModel[]> = {
  anthropic: [AiModel.Opus, AiModel.Sonnet, AiModel.Haiku],
};

type AccountAiSettingsProps = {
  settings?: AiSettings;
  refetch: any;
};

const AccountAiSettings = (props: AccountAiSettingsProps) => {
  const { settings, refetch } = props;
  const [updateUserAiSettings] = useUpdateUserAiSettingsMutation();
  const [provider, setProvider] = useState<string | undefined>(settings?.provider);
  const modelOptions: AiModel[] = provider ? (MODELS[provider] ?? []) : [];

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

  const getProviderLabel = (type: AiProvider | string): string => {
    switch (type) {
      case AiProvider.Anthropic:
        return "Anthropic";
      default:
        return String(type);
    }
  };

  const getModelLabel = (type: AiModel | string): string => {
    switch (type) {
      case AiModel.Opus:
        return "Claude Opus 4.6";
      case AiModel.Sonnet:
        return "Claude Sonnet 4.6";
      case AiModel.Haiku:
        return "Claude Haiku 4.6";
      default:
        return String(type);
    }
  };

  return (
    <DataCard.FormSection
      title={"AI Agents"}
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
        label="Provider"
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
        label="Model"
        options={modelOptions}
        getOptionLabel={getModelLabel}
        visible={(_, __, values) =>
          Boolean(values.enableAI)
        }
        required={(_, __, values) => Boolean(values.enableAI) && provider !== null}
      />
      <TextProperty
        id="apiKey"
        accessor="aiSettings.apiKey"
        label={"API Key"}
        visible={(_, __, values) =>
          Boolean(values.enableAI)
        }
        required
      />
    </DataCard.FormSection>
  );
};

export default AccountAiSettings;
