import Button from "core/components/Button";
import Field from "core/components/forms/Field";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useForm from "core/hooks/useForm";
import { useResetPasswordMutation } from "identity/graphql/mutations.generated";
import { useTranslation } from "next-i18next";
import Image from "next/legacy/image";
import Link from "core/components/Link";
import { ReactElement, useState } from "react";

interface ResetPasswordForm {
  email: string;
}

const PasswordResetPage: NextPageWithLayout = () => {
  const [resetPassword] = useResetPasswordMutation();
  const { t } = useTranslation();
  const [isDone, setDone] = useState(false);

  const form = useForm<ResetPasswordForm>({
    onSubmit: async (values) => {
      const { data } = await resetPassword({
        variables: {
          input: { email: values.email },
        },
      });
      setDone(data?.resetPassword.success ?? false);
    },
    initialState: {},
    validate: (values) => {
      const errors = {} as any;
      if (!values.email) {
        errors.email = "Please enter an email address";
      }
      return errors;
    },
  });

  return (
    <Page title={t("Reset password")}>
      <div className="flex min-h-screen flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="max-w-md">
          <div className="relative mb-6 h-16 w-auto">
            <Image
              priority
              src="/images/logo.svg"
              layout="fill"
              className="mx-auto block h-16 w-auto"
              alt="OpenHEXA logo"
            />
          </div>
          {isDone ? (
            <div className="space-y-6">
              <h2 className="text-center text-3xl font-extrabold text-gray-900">
                Password reset sent
              </h2>
              <p>
                We’ve emailed you instructions for setting your password, if an
                account exists with the email you entered. You should receive
                them shortly.
              </p>
              <p>
                If you don’t receive an email, please make sure you’ve entered
                the address you registered with, and check your spam folder.
              </p>
              <div className="text-center">
                <Link href="/">
                  <Button>Go back to login</Button>
                </Link>
              </div>
            </div>
          ) : (
            <form className="flex-1 space-y-6" onSubmit={form.handleSubmit}>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                Password reset
              </h2>
              <p>
                Forgotten your password? Enter your email address below, and
                we’ll email instructions for setting a new one.
              </p>
              <Field
                name="email"
                type="text"
                label="Email address"
                required
                autoComplete="email"
                value={form.formData.email}
                onChange={form.handleInputChange}
                disabled={form.isSubmitting}
                error={form.touched.email && form.errors.email}
              />
              <Button
                disabled={form.isSubmitting}
                type="submit"
                className="w-full"
              >
                Reset
              </Button>
            </form>
          )}
        </div>
      </div>
    </Page>
  );
};

PasswordResetPage.getLayout = (page: ReactElement) => page;

export const getServerSideProps = createGetServerSideProps({
  getServerSideProps: (ctx) => {
    if (ctx.me?.user) {
      return {
        redirect: {
          permanent: false,
          destination: (ctx.query.next as string) || "/",
        },
      };
    }
  },
});

export default PasswordResetPage;
