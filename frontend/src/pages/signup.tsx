import clsx from "clsx";
import Button from "core/components/Button";
import Link from "core/components/Link";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import Field from "core/components/forms/Field/Field";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useForm from "core/hooks/useForm";
import CenteredLayout from "core/layouts/centered";
import { SignupError } from "graphql/types";
import { useSignupMutation } from "identity/graphql/mutations.generated";
import { useSignupPageQuery } from "identity/graphql/queries.generated";
import { useTranslation } from "next-i18next";
import Image from "next/legacy/image";
import { useRouter } from "next/router";
import { ReactElement, useState } from "react";

interface SignupForm {
  email: string;
}

const SignupPage: NextPageWithLayout = () => {
  const router = useRouter();
  const [signup] = useSignupMutation();
  const { t } = useTranslation();
  const [isSubmitted, setIsSubmitted] = useState(false);

  const { data } = useSignupPageQuery();

  const form = useForm<SignupForm>({
    onSubmit: async (values) => {
      const { data } = await signup({
        variables: {
          input: {
            email: values.email,
          },
        },
      });

      if (data?.signup.success) {
        setIsSubmitted(true);
      } else if (
        data?.signup.errors?.includes(SignupError.SelfRegistrationDisabled)
      ) {
        throw new Error(t("Self-registration is currently disabled."));
      }
    },
    initialState: {},
    validate: (values) => {
      const errors = {} as any;
      if (!values.email) {
        errors.email = t("Please enter an email address");
      } else if (!values.email.includes("@")) {
        errors.email = t("Please enter a valid email address");
      }
      return errors;
    },
  });

  // Redirect to login if self-registration is disabled
  if (data && !data.config?.allowSelfRegistration) {
    router.push("/login").then();
    return null;
  }

  if (isSubmitted) {
    return (
      <Page>
        <div className="max-w-md space-y-6 text-center">
          <div className="relative h-16 w-auto">
            <Image
              priority
              src="/images/logo.svg"
              layout="fill"
              className="mx-auto block h-16 w-auto"
              alt="OpenHEXA logo"
            />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            {t("Check your email")}
          </h2>
          <p className="text-gray-600">
            {t(
              "We've sent a verification link to your email address. Please click the link to complete your registration.",
            )}
          </p>
          <p className="text-sm text-gray-500">
            {t("This link will expire in 48 hours.")}
          </p>
          <div className="pt-4">
            <Link href="/login">
              <Button variant="secondary">{t("Back to login")}</Button>
            </Link>
          </div>
        </div>
      </Page>
    );
  }

  return (
    <Page>
      <form
        className={clsx("max-w-md", "flex-1 space-y-6")}
        onSubmit={form.handleSubmit}
      >
        <div>
          <div className="relative h-16 w-auto">
            <Image
              priority
              src="/images/logo.svg"
              layout="fill"
              className="mx-auto block h-16 w-auto"
              alt="OpenHEXA logo"
            />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {t("Sign up")}
          </h2>
        </div>
        <div className="space-y-4 pt-2">
          <Field
            name="email"
            type="email"
            label={t("Email address")}
            required
            fullWidth
            value={form.formData.email}
            onChange={form.handleInputChange}
            error={form.touched.email && form.errors.email}
          />
          {form.submitError && (
            <div className="text-sm text-red-600">{form.submitError}</div>
          )}
        </div>
        <div className="space-y-2">
          <Button
            data-testid="submit"
            disabled={form.isSubmitting}
            type="submit"
            className="w-full"
          >
            {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
            {t("Sign up")}
          </Button>
        </div>
        <div className="mt-4 text-center text-sm">
          <span className="text-gray-600">{t("Already have an account?")}</span>{" "}
          <Link href="/login" customStyle="text-blue-600 hover:text-blue-500">
            {t("Sign in")}
          </Link>
        </div>
      </form>
    </Page>
  );
};

SignupPage.getLayout = (page: ReactElement) => (
  <CenteredLayout>{page}</CenteredLayout>
);

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  getServerSideProps(ctx) {
    if (ctx.me?.user) {
      return {
        redirect: {
          destination: "/user/account",
          permanent: false,
        },
      };
    }

    return { props: {} };
  },
});

export default SignupPage;
