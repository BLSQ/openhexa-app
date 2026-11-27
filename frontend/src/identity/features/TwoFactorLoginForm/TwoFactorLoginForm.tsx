import { useApolloClient } from "@apollo/client";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import { getSafeRedirectPath } from "core/helpers/redirect";
import useForm from "core/hooks/useForm";
import OtpCodeFields from "identity/features/OtpCodeFields";
import {
  useGenerateChallengeMutation,
  useVerifyTwoFactorLoginMutation,
} from "identity/graphql/mutations.generated";
import { logout } from "identity/helpers/auth";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useRef } from "react";
import { toast } from "react-toastify";

interface TwoFactorLoginFormValues {
  token: string;
}

const TwoFactorLoginForm = () => {
  const router = useRouter();
  const { t } = useTranslation();
  const [generateChallenge] = useGenerateChallengeMutation();
  const [verifyTwoFactorLogin] = useVerifyTwoFactorLoginMutation();
  const client = useApolloClient();
  // Guards against React strict mode running the effect twice, which would
  // send two emails with different codes.
  const codeSent = useRef(false);

  useEffect(() => {
    if (!codeSent.current) {
      codeSent.current = true;
      generateChallenge();
    }
  }, [generateChallenge]);

  const form = useForm<TwoFactorLoginFormValues>({
    onSubmit: async (values) => {
      const { data } = await verifyTwoFactorLogin({
        variables: { input: { token: values.token } },
      });
      if (data?.verifyTwoFactorLogin.success) {
        await router.push(getSafeRedirectPath(router.query.next));
        return;
      }
      form.setFieldValue("token", "");
      throw new Error(t("Invalid token"));
    },
    initialState: { token: "" },
    validate: (values) => {
      const errors = {} as any;
      if (!values.token) {
        errors.token = t("Enter the token");
      }
      return errors;
    },
  });

  // Logging out sends the browser back to /login without a reload: the cached
  // "twoFactorPending" must be dropped or this form would keep showing.
  const useAnotherAccount = async () => {
    await logout();
    await client.resetStore();
  };

  const sendNewCode = async () => {
    form.setFieldValue("token", "");
    await generateChallenge();
    toast.success(t("A new code has been sent to your mailbox."));
  };

  return (
    <form
      className="space-y-6"
      data-testid="two-factor-login-form"
      onSubmit={form.handleSubmit}
    >
      <OtpCodeFields
        value={form.formData.token}
        onChange={form.handleInputChange}
        error={form.submitError}
        onSendNewCode={sendNewCode}
      />
      <div className="space-y-2">
        <Button
          data-testid="submit"
          disabled={form.isSubmitting}
          type="submit"
          className="w-full"
        >
          {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Sign in")}
        </Button>
        <Button
          variant="secondary"
          type="button"
          size="sm"
          className="w-full"
          onClick={useAnotherAccount}
        >
          {t("Use another account")}
        </Button>
      </div>
    </form>
  );
};

export default TwoFactorLoginForm;
