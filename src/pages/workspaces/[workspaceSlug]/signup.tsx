import Spinner from "core/components/Spinner";
import Button from "core/components/Button";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useForm from "core/hooks/useForm";
import Image from "next/legacy/image";
import CenteredLayout from "core/layouts/centered";
import { useRouter } from "next/router";
import { ReactElement } from "react";
import Page from "core/components/Page";

import Field from "core/components/forms/Field";
import clsx from "clsx";
import { useJoinWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import { JoinWorkspaceError } from "graphql-types";
import { useTranslation } from "react-i18next";

type Props = {
  email: string;
  token: string;
};

interface WorkspaceSignUpForm {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  confirmPassword: string;
  token: string;
}

const WorkspaceSignUpPage: NextPageWithLayout = (props: Props) => {
  const router = useRouter();
  const { t } = useTranslation();
  const { email, token } = props;

  const [joinWorkspace] = useJoinWorkspaceMutation();

  const form = useForm<WorkspaceSignUpForm>({
    onSubmit: async (values) => {
      const { email, ...formData } = values;
      const { data } = await joinWorkspace({
        variables: {
          input: {
            ...formData,
            token,
          },
        },
      });
      if (!data) {
        throw new Error("An unexpected error happened. Please retry later.");
      }
      const { success, errors, workspace } = data.joinWorkspace;
      if (success && workspace) {
        await router.push(`/workspaces/${encodeURIComponent(workspace.slug)}`);
      } else if (errors.includes(JoinWorkspaceError.InvalidCredentials)) {
        throw new Error(t("Invalid password format"));
      } else if (
        errors.some(
          (x) =>
            x === JoinWorkspaceError.AlreadyExists ||
            x === JoinWorkspaceError.AuthenticationRequired,
        )
      ) {
        throw new Error(
          t(
            "An account already exists with this email address. Please go to the login page.",
          ),
        );
      } else if (errors.includes(JoinWorkspaceError.PermissionDenied)) {
        throw new Error(
          t("You don't have the permission to join this workspace."),
        );
      } else if (
        errors.some(
          (x) =>
            x === JoinWorkspaceError.InvalidToken ||
            x === JoinWorkspaceError.InvitationNotFound,
        )
      ) {
        throw new Error(t("The invite link is invalid."));
      }
    },
    initialState: {
      email,
    },
    validate: (values) => {
      const errors = {} as any;
      if (!values.firstName) {
        errors.firstName = t("Enter your first name");
      }
      if (!values.lastName) {
        errors.lastName = t("Enter your last name");
      }
      if (!values.password) {
        errors.password = t("Enter your password");
      }
      if (!values.confirmPassword) {
        errors.password = t("Enter the password confirmation");
      }

      if (
        values.password &&
        values.confirmPassword &&
        values.password !== values.confirmPassword
      ) {
        errors.confirmPassword = t(
          "The password confirmation does not match the given password",
        );
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
              src="/images/logo.svg"
              layout="fill"
              className="mx-auto block h-16 w-auto"
              alt="OpenHexa logo"
            />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {t("Sign up")}
          </h2>
        </div>

        <div className="space-y-4 pt-2">
          <Field
            name="email"
            required
            type="email"
            label={t("Email")}
            value={form.formData.email}
            disabled
          />
          <Field
            name="firstName"
            required
            data-testid="firstName"
            label={t("First name")}
            value={form.formData.firstName}
            disabled={form.isSubmitting}
            error={form.touched.firstName && form.errors.firstName}
            onChange={form.handleInputChange}
          />
          <Field
            name="lastName"
            required
            data-testid="lastName"
            label={t("Last name")}
            value={form.formData.lastName}
            disabled={form.isSubmitting}
            error={form.touched.lastName && form.errors.lastName}
            onChange={form.handleInputChange}
          />
          <div>
            <Field
              name="password"
              type="password"
              required
              data-testid="password"
              label={t("Password")}
              value={form.formData.password}
              disabled={form.isSubmitting}
              error={form.touched.password && form.errors.password}
              onChange={form.handleInputChange}
            />
          </div>
          <Field
            name="confirmPassword"
            required
            type="password"
            data-testid="confirmPassword"
            label={t("Confirm password")}
            value={form.formData.confirmPassword}
            disabled={form.isSubmitting}
            error={form.touched.confirmPassword && form.errors.confirmPassword}
            onChange={form.handleInputChange}
          />
          <p className="mt-2 text-xs">
            <span>
              {t("The password must respect the following criterias:")}
            </span>
          </p>
          <ul className="list my-2 list-inside list-disc text-xs">
            <li>{t("At least 8 characters.")}</li>
            <li>{t("Alphanumeric (can't be entirely numeric)")}.</li>
            <li>
              {t(
                "Can't be a commonly used password or similar to your personal information",
              )}
            </li>
          </ul>
          {form.submitError && (
            <p data-testid="error" className={"my-2 text-sm text-red-600"}>
              {form.submitError}
            </p>
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
            {t("Submit")}
          </Button>
        </div>
      </form>
    </Page>
  );
};

WorkspaceSignUpPage.getLayout = (page: ReactElement) => (
  <CenteredLayout>{page}</CenteredLayout>
);

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  async getServerSideProps(ctx, client) {
    const { token, email } = ctx.query;
    if (!token || !email) {
      return {
        notFound: true,
      };
    }
    return {
      props: {
        email,
        token,
      },
    };
  },
});

export default WorkspaceSignUpPage;
