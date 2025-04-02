import Button from "core/components/Button";
import Field from "core/components/forms/Field";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import useForm from "core/hooks/useForm";
import { SetPasswordError } from "graphql/types";
import { useSetPasswordMutation } from "identity/graphql/mutations.generated";
import Link from "core/components/Link";
import { useRouter } from "next/router";
import { useState } from "react";
import { useTranslation } from "next-i18next";

type Form = {
  password1: string;
  password2: string;
};

function getErrorMessage(error: SetPasswordError) {
  switch (error) {
    case SetPasswordError.InvalidPassword:
      return "Invalid password";
    case SetPasswordError.InvalidToken:
      return "Invalid token";
    case SetPasswordError.PasswordMismatch:
      return "Passwords are not the same";
    case SetPasswordError.UserNotFound:
      return "No matching user";
  }
}

const SetPasswordPage = () => {
  const router = useRouter();
  const [setPassword] = useSetPasswordMutation();
  const [isDone, setDone] = useState(false);
  const { t } = useTranslation();
  const form = useForm<Form>({
    onSubmit: async (values) => {
      if (router.query.tokens) {
        const { data } = await setPassword({
          variables: {
            input: {
              password1: values.password1,
              password2: values.password2,
              uidb64: router.query.tokens[0],
              token: router.query.tokens[1],
            },
          },
        });

        if (data?.setPassword.error) {
          throw new Error(getErrorMessage(data.setPassword.error));
        }

        setDone(data?.setPassword.success ?? false);
      }
    },
    validate: (values) => {
      const errors = {} as any;
      if (!values.password1) {
        errors.password1 = t("Enter a password");
      }
      if (!values.password2) {
        errors.password2 = t("Enter a password");
      }
      if (
        values.password1 &&
        values.password2 &&
        values.password1 !== values.password2
      ) {
        errors.password2 = t("Passwords are not the same");
      }
      return errors;
    },
  });

  return (
    <Page>
      <div className="flex min-h-screen flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="max-w-md">
          {isDone ? (
            <>
              <h2 className="mb-6 text-center text-3xl font-extrabold text-gray-900">
                {t("Password changed!")}
              </h2>
              <div className="text-center">
                <Link href="/">
                  <Button>{t("Go back to login")}</Button>
                </Link>
              </div>
            </>
          ) : (
            <form className="flex-1 space-y-6" onSubmit={form.handleSubmit}>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                {t("Set a new password")}
              </h2>
              <Field
                name="password1"
                type="password"
                label={t("Password")}
                required
                autoComplete="new-password"
                value={form.formData.password1}
                onChange={form.handleInputChange}
                disabled={form.isSubmitting}
                error={form.touched.password1 && form.errors.password1}
              />
              <Field
                name="password2"
                type="password"
                label={t("Password")}
                required
                autoComplete="new-password"
                value={form.formData.password2}
                onChange={form.handleInputChange}
                disabled={form.isSubmitting}
                error={form.touched.password2 && form.errors.password2}
              />
              {form.submitError && (
                <p className={"mt-2 text-sm text-red-600"}>
                  {form.submitError}
                </p>
              )}
              <Button
                disabled={form.isSubmitting}
                type="submit"
                className="w-full"
              >
                {t("Set password")}
              </Button>
            </form>
          )}
        </div>
      </div>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
});

export default SetPasswordPage;
