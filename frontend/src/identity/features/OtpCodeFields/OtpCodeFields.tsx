import Field from "core/components/forms/Field";
import { useTranslation } from "next-i18next";
import { ChangeEventHandler } from "react";

type OtpCodeFieldsProps = {
  value?: string;
  onChange: ChangeEventHandler<HTMLInputElement>;
  error?: string | null;
  onSendNewCode: () => void;
};

const OtpCodeFields = ({
  value,
  onChange,
  error,
  onSendNewCode,
}: OtpCodeFieldsProps) => {
  const { t } = useTranslation();

  return (
    <>
      <p className="text-gray-600">
        {t("Enter the OTP code you received in your mailbox.")}
      </p>
      <Field
        fullWidth
        name="token"
        data-testid="token"
        label={t("OTP Code")}
        value={value}
        placeholder="123456"
        onChange={onChange}
        required
      />
      <div className="my-2 flex items-center justify-between gap-2">
        {error && (
          <div data-testid="error" className="text-sm text-red-600">
            <span>{error}</span>
          </div>
        )}
        <button type="button" className="text-blue-600" onClick={onSendNewCode}>
          {t("Send a new code")}
        </button>
      </div>
    </>
  );
};

export default OtpCodeFields;
