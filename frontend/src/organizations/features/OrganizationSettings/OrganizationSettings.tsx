import { useState } from "react";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import DataCard from "core/components/DataCard";
import { OrganizationQuery } from "organizations/graphql/queries.generated";
import { useUpdateOrganizationSettingsMutation } from "./OrganizationSettings.generated";
import Block from "core/components/Block";
import Button from "core/components/Button";

type OrganizationSettingsProps = {
  organization: OrganizationQuery["organization"];
};

const OrganizationSettings = ({ organization }: OrganizationSettingsProps) => {
  const { t } = useTranslation();
  const [updateSettings, { loading }] = useUpdateOrganizationSettingsMutation();
  const [logo, setLogo] = useState(organization?.logo || "");
  const [icon, setIcon] = useState(organization?.icon || "");

  if (!organization) {
    return null;
  }

  const handleSave = async () => {
    try {
      const { data } = await updateSettings({
        variables: {
          input: {
            organizationId: organization.id,
            logo: logo || null,
            icon: icon || null,
          },
        },
      });

      if (data?.updateOrganizationSettings?.success) {
        toast.success(t("Settings updated successfully"));
      } else {
        const errors = data?.updateOrganizationSettings?.errors || [];
        if (errors.includes("PERMISSION_DENIED")) {
          toast.error(t("You don't have permission to update settings"));
        } else if (errors.includes("NOT_FOUND")) {
          toast.error(t("Organization not found"));
        } else {
          toast.error(t("Failed to update settings"));
        }
      }
    } catch (error) {
      toast.error(t("Failed to update settings"));
    }
  };

  return (
    <Block>
      <DataCard>
        <DataCard.Section>
          <DataCard.Header>
            <h2 className="text-xl font-semibold">{t("Organization Logo")}</h2>
            <p className="text-sm text-gray-500 mt-1">
              {t(
                "Upload an SVG logo that will be displayed in pipeline template listings",
              )}
            </p>
          </DataCard.Header>
          <div className="space-y-4">
            {logo && (
              <div className="border border-gray-200 rounded p-4 bg-gray-50">
                <div className="text-sm text-gray-600 mb-2">{t("Preview:")}</div>
                <div
                  className="h-12 flex items-center"
                  dangerouslySetInnerHTML={{ __html: logo }}
                />
              </div>
            )}
            <div>
              <label
                htmlFor="logo"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                {t("SVG Content")}
              </label>
              <textarea
                id="logo"
                rows={6}
                className="w-full border border-gray-300 rounded px-3 py-2 font-mono text-sm"
                value={logo}
                onChange={(e) => setLogo(e.target.value)}
                placeholder={t("Paste your SVG content here...")}
              />
            </div>
          </div>
        </DataCard.Section>

        <DataCard.Section>
          <DataCard.Header>
            <h2 className="text-xl font-semibold">{t("Organization Icon")}</h2>
            <p className="text-sm text-gray-500 mt-1">
              {t(
                "Upload an SVG icon that will be displayed in organization listings",
              )}
            </p>
          </DataCard.Header>
          <div className="space-y-4">
            {icon && (
              <div className="border border-gray-200 rounded p-4 bg-gray-50">
                <div className="text-sm text-gray-600 mb-2">{t("Preview:")}</div>
                <div
                  className="h-12 flex items-center"
                  dangerouslySetInnerHTML={{ __html: icon }}
                />
              </div>
            )}
            <div>
              <label
                htmlFor="icon"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                {t("SVG Content")}
              </label>
              <textarea
                id="icon"
                rows={6}
                className="w-full border border-gray-300 rounded px-3 py-2 font-mono text-sm"
                value={icon}
                onChange={(e) => setIcon(e.target.value)}
                placeholder={t("Paste your SVG content here...")}
              />
            </div>
          </div>
        </DataCard.Section>

        <DataCard.Section>
          <div className="flex justify-end">
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={loading}
            >
              {loading ? t("Saving...") : t("Save Settings")}
            </Button>
          </div>
        </DataCard.Section>
      </DataCard>
    </Block>
  );
};

export default OrganizationSettings;
