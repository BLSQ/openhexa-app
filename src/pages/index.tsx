import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";
import Button from "core/components/Button";
import { useLoginMutation } from "core/graphql/mutations.generated";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useForm from "core/hooks/useForm";
import Image from "next/image";
import Link from "core/components/Link";
import { useRouter } from "next/router";
import { ReactElement } from "react";
import Page from "core/components/Layout/Page";
import { useTranslation } from "next-i18next";

interface LoginForm {
  email: string;
  password: string;
}

const LoginPage: NextPageWithLayout = () => {
  const router = useRouter();
  const [doLogin] = useLoginMutation();
  const { t } = useTranslation();

  const form = useForm<LoginForm>({
    onSubmit: async (values) => {
      const { data } = await doLogin({
        variables: {
          input: { email: values.email, password: values.password },
        },
      });
      if (data?.login.success) {
        router.push((router.query.next as string) ?? "/dashboard");
      } else {
        throw new Error(t("Wrong email address and/or password."));
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
      return errors;
    },
  });

  return (
    <Page>
      <div className="flex min-h-screen items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <form
          className="max-w-md flex-1 space-y-6"
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
              Sign in
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              No account yet?{" "}
              <a
                href="mailto:pvanliefland@bluesquarehub.com?subject=Hexa: access request"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Contact us!
              </a>
            </p>
          </div>
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
          <Button
            data-testid="submit"
            disabled={form.isSubmitting || !form.isValid}
            type="submit"
            className="w-full"
          >
            {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
            {t("Sign in")}
          </Button>
        </form>
      </div>
    </Page>
  );
};

LoginPage.getLayout = (page: ReactElement) => page;

export const getServerSideProps = createGetServerSideProps({
  getServerSideProps: (ctx) => {
    if (ctx.me?.user) {
      return {
        redirect: {
          permanent: false,
          destination: (ctx.query.next as string) || "/dashboard",
        },
      };
    }
  },
});

export default LoginPage;
