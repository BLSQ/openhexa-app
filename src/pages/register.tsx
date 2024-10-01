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
import { RegisterError } from "graphql/types";
import { useRegisterMutation } from "identity/graphql/mutations.generated";
import { useRegisterPageQuery } from "identity/graphql/queries.generated";
import { useTranslation } from "next-i18next";
import Image from "next/legacy/image";
import { useRouter } from "next/router";
import { ReactElement } from "react";

interface RegisterForm {
  firstName: string;
  lastName: string;
  password1: string;
  password2: string;
}

const RegisterPage: NextPageWithLayout = (props: {
  token: string;
  email: string;
}) => {
  const { email, token } = props;
  const router = useRouter();
  const [register] = useRegisterMutation();
  const { t } = useTranslation();

  const { data } = useRegisterPageQuery();

  const form = useForm<RegisterForm>({
    onSubmit: async (values) => {
      const { data } = await register({
        variables: {
          input: {
            invitationToken: token,
            password1: values.password1,
            password2: values.password2,
            firstName: values.firstName,
            lastName: values.lastName,
          },
        },
      });

      if (data?.register.success) {
        // Redirect the user to the workspace's invitations page
        await router.push("/user/account");
      } else if (
        data?.register.errors?.includes(RegisterError.InvalidPassword)
      ) {
        throw new Error(t("Invalid password"));
      } else if (data?.register.errors?.includes(RegisterError.InvalidToken)) {
        throw new Error(
          t(
            "You cannot register an account with this link. Please contact the person that invited you to receive a new link.",
          ),
        );
      } else if (
        data?.register.errors?.includes(RegisterError.PasswordMismatch)
      ) {
        throw new Error(t("The two passwords are not the same."));
      } else if (data?.register.errors?.includes(RegisterError.EmailTaken)) {
        throw new Error(
          t("This email address is already taken. Please login instead."),
        );
      }
    },
    initialState: {},
    validate: (values) => {
      const errors = {} as any;
      if (values.password1 !== values.password2) {
        errors.password2 = t("The two passwords are not the same");
      }
      return errors;
    },
  });

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
              src="/images/logo_with_text_black.svg"
              layout="fill"
              className="mx-auto block h-16 w-auto"
              alt="OpenHexa logo"
            />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {t("Create your account")}
          </h2>
          <p className="text-center mt-2">
            {t("Already have an account?")}&nbsp;
            <Link href="/login">{t("Go to login page")}</Link>
          </p>
        </div>
        <div className=" pt-2 space-y-4">
          <Field
            name="email"
            label={t("Email address")}
            required
            disabled
            fullWidth
            help={t(
              "You cannot change your email address. It's the one you've been invited with",
            )}
            value={email}
          />
          <Field
            name="firstName"
            label={t("First name")}
            required
            fullWidth
            value={form.formData.firstName}
            onChange={form.handleInputChange}
            error={form.errors.firstName}
          />
          <Field
            name="lastName"
            label={t("Last name")}
            required
            fullWidth
            value={form.formData.lastName}
            onChange={form.handleInputChange}
            error={form.errors.lastName}
          />
          <Field
            name="password1"
            type="password"
            required
            fullWidth
            label={t("Password")}
            value={form.formData.password1}
            onChange={form.handleInputChange}
            help={
              <ul>
                {data?.config?.passwordRequirements?.map((el, i) => (
                  <li key={i}>{el}</li>
                ))}
              </ul>
            }
            error={form.errors.password1}
          />
          <Field
            name="password2"
            type="password"
            required
            fullWidth
            label={t("Confirm Password")}
            value={form.formData.password2}
            onChange={form.handleInputChange}
            error={form.errors.password2}
          />
          <div className="text-red-500">{form.submitError}</div>
        </div>
        <div className="space-y-2">
          <Button
            data-testid="submit"
            disabled={form.isSubmitting}
            type="submit"
            className="w-full"
          >
            {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
            {t("Create account")}
          </Button>
        </div>
      </form>
    </Page>
  );
};

RegisterPage.getLayout = (page: ReactElement) => (
  <CenteredLayout>{page}</CenteredLayout>
);

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  getServerSideProps(ctx, client) {
    if (ctx.me?.user) {
      return {
        redirect: {
          destination: "/user/account",
          permanent: false,
        },
      };
    }

    if (!ctx.query.token || !ctx.query.email) {
      return {
        redirect: {
          destination: "/login",
          permanent: false,
        },
      };
    }

    return {
      props: {
        token: ctx.query.token,
        email: ctx.query.email,
      },
    };
  },
});

export default RegisterPage;
