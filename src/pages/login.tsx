import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";
import Button from "core/components/Button";
import { useLoginMutation } from "identity/graphql/mutations.generated";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useForm from "core/hooks/useForm";
import Image from "next/legacy/image";
import Link from "core/components/Link";
import CenteredLayout from "core/layouts/centered";
import { useRouter } from "next/router";
import { ReactElement, useState } from "react";
import Page from "core/components/Page";
import { useTranslation } from "next-i18next";
import { LoginError } from "graphql-types";
import { generateChallenge } from "identity/helpers/auth";
import Field from "core/components/forms/Field";
import clsx from "clsx";

interface LoginForm {
  email: string;
  password: string;
  token?: string;
}

const LoginPage: NextPageWithLayout = () => {
  const router = useRouter();
  const [doLogin] = useLoginMutation();
  const [showOTPForm, setOTPForm] = useState(false);
  const { t } = useTranslation();

  const form = useForm<LoginForm>({
    onSubmit: async (values) => {
      const { data } = await doLogin({
        variables: {
          input: {
            email: values.email,
            password: values.password,
            token: values.token,
          },
        },
      });
      if (!data) {
        throw new Error(t("An unexpected error ocurred."));
      }
      if (data.login.success) {
        await router.push((router.query.next as string) ?? "/");
      } else if (
        data.login.errors?.some(
          (error) => error === LoginError.InvalidCredentials
        )
      ) {
        throw new Error(t("Wrong email address and/or password."));
      } else if (
        data.login.errors?.some((error) => error === LoginError.InvalidOtp)
      ) {
        throw new Error(t("Invalid token"));
      } else if (
        data.login.errors?.some((error) => error === LoginError.OtpRequired)
      ) {
        setOTPForm(true);
      }
    },
    initialState: {},
    validate: (values) => {
      const errors = {} as any;
      if (!values.email) {
        errors.email = t("Please enter an email address");
      }
      if (!values.password) {
        errors.password = t("Enter your password");
      }
      if (!values.token && showOTPForm) {
        errors.token = t("Enter the token");
      }
      return errors;
    },
  });

  return (
    <Page>
      <form
        className={clsx(
          showOTPForm ? "max-w-xs" : "max-w-md",
          "flex-1 space-y-6"
        )}
        onSubmit={form.handleSubmit}
      >
        <div>
          <div className="relative h-16 w-auto">
            <Image
              priority
              src="/images/logo.svg"
              layout="fill"
              className="mx-auto block h-16 w-auto"
              alt="OpenHexa logo"
            />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {t("Sign in")}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {t("No account yet?")}&nbsp;
            <a
              href="mailto:pvanliefland@bluesquarehub.com?subject=Hexa: access request"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              {t("Contact us!")}
            </a>
          </p>
        </div>
        {showOTPForm ? (
          <>
            <div className=" text-gray-600">
              <p>{t("Enter the OTP code you received in your mailbox.")}</p>
            </div>
            <Field
              name="token"
              data-testid="token"
              label={t("OTP Code")}
              value={form.formData.token}
              placeholder="123456"
              onChange={form.handleInputChange}
              required
            />
            {form.submitError && (
              <div
                data-testid="error"
                className="my-2 flex items-center justify-between gap-2 text-sm text-red-600"
              >
                <span>{form.submitError}</span>
                <button
                  type="button"
                  className="text-blue-600"
                  onClick={() => generateChallenge()}
                >
                  {t("Send a new code")}
                </button>
              </div>
            )}
          </>
        ) : (
          <>
            <div className="-space-y-px pt-2">
              <label className="sr-only" htmlFor="email">
                {t("Email address")}
              </label>
              <Input
                name="email"
                data-testid="email"
                value={form.formData.email}
                required
                type="text"
                className="rounded-b-none"
                onChange={form.handleInputChange}
                autoComplete="email"
                placeholder={t("Email address")}
                disabled={form.isSubmitting}
                error={form.touched.email && form.errors.email}
              />
              <label className="sr-only" htmlFor="password">
                {t("Password")}
              </label>
              <Input
                name="password"
                value={form.formData.password}
                required
                data-testid="password"
                type="password"
                placeholder={t("Password")}
                onChange={form.handleInputChange}
                autoComplete="current-password"
                disabled={form.isSubmitting}
                error={form.touched.password && form.errors.password}
                className="rounded-t-none"
              />
              {form.submitError && (
                <p data-testid="error" className={"my-2 text-sm text-red-600"}>
                  {form.submitError}
                </p>
              )}
            </div>
            <div className="flex items-center justify-end">
              <div className="text-sm">
                <Link
                  href="/auth/password_reset/"
                  customStyle="text-blue-600 hover:text-blue-500"
                >
                  {t("Forgot your password?")}
                </Link>
              </div>
            </div>
          </>
        )}
        <div className="space-y-2">
          <Button
            data-testid="submit"
            disabled={form.isSubmitting || !form.isValid}
            type="submit"
            className="w-full"
          >
            {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
            {t("Sign in")}
          </Button>
          {showOTPForm && (
            <Button
              variant="secondary"
              type="reset"
              size="sm"
              className="w-full"
              onClick={() => setOTPForm(false)}
            >
              {t("Back")}
            </Button>
          )}
        </div>
      </form>
    </Page>
  );
};

LoginPage.getLayout = (page: ReactElement) => (
  <CenteredLayout>{page}</CenteredLayout>
);

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
});

export default LoginPage;
