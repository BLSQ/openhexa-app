import { useState, ChangeEvent, FormEvent } from "react";
import { useTranslation } from "next-i18next";
import { Organization_OrganizationFragment } from "organizations/graphql/queries.generated";
import { useUpdateOrganizationMutation } from "organizations/graphql/mutations.generated";
import Field from "core/components/forms/Field";
import Input from "core/components/forms/Input";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import { UpdateOrganizationError } from "graphql/types";
import { PencilIcon } from "@heroicons/react/24/outline";
import DeleteOrganizationDialog from "./DeleteOrganizationDialog";
import { toast } from "react-toastify";
import { resizeImage } from "core/helpers/image";

type OrganizationSettingsProps = {
  organization: Organization_OrganizationFragment;
};

const OrganizationSettings = ({ organization }: OrganizationSettingsProps) => {
  const { t } = useTranslation();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(organization.name);
  const [shortName, setShortName] = useState(organization.shortName || "");
  const [logoDataUrl, setLogoDataUrl] = useState<string | null>(
    organization.logo ? `data:image/png;base64,${organization.logo}` : null,
  );
  const [logoChanged, setLogoChanged] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [nameError, setNameError] = useState("");
  const [shortNameError, setShortNameError] = useState("");

  const [updateOrganization] = useUpdateOrganizationMutation();

  const handleLogoChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const resizedDataUrl = await resizeImage(file, 200, 200);
      setLogoDataUrl(resizedDataUrl);
      setLogoChanged(true);
    }
  };

  const handleRemoveLogo = () => {
    setLogoDataUrl(null);
    setLogoChanged(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setName(organization.name);
    setShortName(organization.shortName || "");
    setLogoDataUrl(
      organization.logo ? `data:image/png;base64,${organization.logo}` : null,
    );
    setLogoChanged(false);
    setError("");
    setNameError("");
    setShortNameError("");
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError("");
    setNameError("");
    setShortNameError("");

    if (!name.trim()) {
      setNameError(t("Organization name is required"));
      setIsSubmitting(false);
      return;
    }

    if (shortName.trim()) {
      const trimmedShortName = shortName.trim();
      if (trimmedShortName.length > 5) {
        setShortNameError(t("Short name must be maximum 5 characters"));
        setIsSubmitting(false);
        return;
      }
      if (!/^[A-Z]+$/.test(trimmedShortName)) {
        setShortNameError(t("Short name must contain only uppercase letters"));
        setIsSubmitting(false);
        return;
      }
    }

    try {
      const { data: result } = await updateOrganization({
        variables: {
          input: {
            id: organization.id,
            name: name.trim(),
            ...(shortName.trim() && { shortName: shortName.trim() }),
            ...(logoChanged && { logo: logoDataUrl || "" }),
          },
        },
        refetchQueries: ["Organization"],
      });

      if (result?.updateOrganization.success) {
        toast.success(t("Organization updated successfully"));
        setIsEditing(false);
        setLogoChanged(false);
      } else {
        const errors = result?.updateOrganization.errors ?? [];
        if (errors.includes(UpdateOrganizationError.NameDuplicate)) {
          setNameError(t("An organization with this name already exists"));
        } else if (
          errors.includes(UpdateOrganizationError.ShortNameDuplicate)
        ) {
          setShortNameError(
            t("An organization with this short name already exists"),
          );
        } else if (errors.includes(UpdateOrganizationError.InvalidShortName)) {
          setShortNameError(
            t("Short name must be maximum 5 uppercase letters"),
          );
        } else if (errors.includes(UpdateOrganizationError.InvalidLogo)) {
          setError(t("The logo format is invalid. Please try another image."));
        } else if (errors.includes(UpdateOrganizationError.PermissionDenied)) {
          setError(t("You don't have permission to update this organization"));
        } else {
          setError(t("An error occurred while updating the organization"));
        }
      }
    } catch (err) {
      setError(t("An error occurred while updating the organization"));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            {t("General")}
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            {t("Manage your organization's name and logo")}
          </p>
        </div>
        {!isEditing && organization.permissions.update && (
          <Button
            variant="white"
            onClick={() => setIsEditing(true)}
            className="flex items-center gap-2"
          >
            <PencilIcon className="w-4 h-4" />
            {t("Edit")}
          </Button>
        )}
      </div>

      <div className="px-6 py-6">
        {!isEditing ? (
          <div className="space-y-6">
            <div>
              <dt className="text-sm font-medium text-gray-500 mb-2">
                {t("Organization Name")}
              </dt>
              <dd className="text-base text-gray-900 break-words">
                {organization.name}
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500 mb-2">
                {t("Short Name")}
              </dt>
              <dd className="text-base text-gray-900">
                {organization.shortName || (
                  <span className="text-gray-400">{t("Not set")}</span>
                )}
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500 mb-2">
                {t("Organization Logo")}
              </dt>
              <dd>
                {organization.logo ? (
                  <img
                    src={`data:image/png;base64,${organization.logo}`}
                    alt={t("Organization logo")}
                    className="h-24 w-24 object-contain rounded border border-gray-200"
                  />
                ) : (
                  <div className="h-24 w-24 bg-gray-100 rounded border border-gray-200 flex items-center justify-center">
                    <span className="text-gray-400 text-sm">
                      {t("No logo")}
                    </span>
                  </div>
                )}
              </dd>
            </div>

            {organization.permissions.delete &&
              organization.shortName !== "BLSQ" && (
                <DeleteOrganizationDialog organization={organization} />
              )}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <Field
              label={t("Organization Name")}
              name="name"
              required
              error={nameError}
            >
              <Input
                type="text"
                value={name}
                className="w-full"
                onChange={(e) => setName(e.target.value)}
                placeholder={t("Enter organization name")}
              />
            </Field>

            <Field
              label={t("Short Name")}
              name="shortName"
              error={shortNameError}
              help={t("Maximum 5 uppercase letters (e.g., WHO, BLSQ)")}
              required
            >
              <Input
                type="text"
                value={shortName}
                className="w-full uppercase"
                onChange={(e) => setShortName(e.target.value.toUpperCase())}
                placeholder={t("Enter short name")}
                maxLength={5}
              />
            </Field>

            <Field label={t("Organization Logo")} name="logo" required>
              <div className="space-y-4">
                {logoDataUrl && (
                  <div className="relative inline-block">
                    <img
                      src={logoDataUrl}
                      alt={t("Organization logo")}
                      className="h-32 w-32 object-contain rounded border border-gray-300"
                    />
                    <button
                      type="button"
                      onClick={handleRemoveLogo}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </div>
                )}
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleLogoChange}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded file:border-0
                    file:text-sm file:font-semibold
                    file:bg-indigo-50 file:text-indigo-700
                    hover:file:bg-indigo-100"
                />
              </div>
            </Field>

            {error && (
              <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded p-3">
                {error}
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <Button
                type="button"
                variant="white"
                onClick={handleCancel}
                disabled={isSubmitting}
              >
                {t("Cancel")}
              </Button>
              <Button type="submit" variant="primary" disabled={isSubmitting}>
                {isSubmitting ? <Spinner size="xs" /> : t("Save Changes")}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default OrganizationSettings;
