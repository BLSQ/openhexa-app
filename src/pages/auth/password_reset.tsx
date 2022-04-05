import { gql } from "@apollo/client";
import Button from "components/Button";
import Field from "components/forms/Field";
import useForm from "hooks/useForm";
import { useResetPasswordMutation } from "libs/graphql";
import { createGetServerSideProps } from "libs/page";
import { NextPageWithLayout } from "libs/types";
import Image from "next/image";
import Link from "next/link";
import { ReactElement, useState } from "react";

interface ResetPasswordForm {
  email: string;
}

const RESET_PASSWORD_MUTATION = gql`
  mutation ResetPassword($input: ResetPasswordInput!) {
    resetPassword(input: $input) {
      success
    }
  }
`;

const PasswordResetPage: NextPageWithLayout = () => {
  const [resetPassword] = useResetPasswordMutation();
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
    <div className="flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 min-h-screen">
      <div className="max-w-md">
        <div className="h-16 w-auto relative mb-6">
          <Image
            priority
            src="/images/logo.svg"
            layout="fill"
            className="block mx-auto h-16 w-auto"
            alt="OpenHexa logo"
          />
        </div>
        {isDone ? (
          <div className="space-y-6">
            <h2 className="text-center text-3xl font-extrabold text-gray-900">
              Password reset sent
            </h2>
            <p>
              We’ve emailed you instructions for setting your password, if an
              account exists with the email you entered. You should receive them
              shortly.
            </p>
            <p>
              If you don’t receive an email, please make sure you’ve entered the
              address you registered with, and check your spam folder.
            </p>
            <div className="text-center">
              <Link href="/">
                <a>
                  <Button>Go back to login</Button>
                </a>
              </Link>
            </div>
          </div>
        ) : (
          <form className="flex-1 space-y-6" onSubmit={form.handleSubmit}>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Password reset
            </h2>
            <p>
              Forgotten your password? Enter your email address below, and we’ll
              email instructions for setting a new one.
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
  );
};

PasswordResetPage.getLayout = (page: ReactElement) => page;

export const getServerSideProps = createGetServerSideProps({
  getServerSideProps: (ctx) => {
    if (ctx.user) {
      return {
        redirect: {
          permanent: false,
          destination: (ctx.query.next as string) || "/dashboard",
        },
      };
    }
  },
});

export default PasswordResetPage;
