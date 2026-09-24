import Button from "core/components/Button";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import CenteredLayout from "core/layouts/centered";
import MCPPermissionMatrix, {
  MCPGrant,
} from "mcp/features/MCPPermissionMatrix";
import { useAuthorizeMcpConnectionMutation } from "mcp/graphql/mutations.generated";
import {
  McpAuthorizationRequestDocument,
  McpAuthorizationRequestQuery,
} from "mcp/graphql/queries.generated";
import { GetServerSidePropsContext } from "next";
import Image from "next/legacy/image";
import { useTranslation } from "next-i18next";
import logo from "public/images/logo.svg";
import { ReactElement, useRef, useState } from "react";

const WORKSPACES_PAGE_SIZE = 100;

const OAUTH_FIELDS = [
  "client_id",
  "redirect_uri",
  "response_type",
  "scope",
  "state",
  "nonce",
  "code_challenge",
  "code_challenge_method",
  "claims",
] as const;

type OAuthParams = Partial<Record<(typeof OAUTH_FIELDS)[number], string>>;

type AuthorizationRequest = NonNullable<
  McpAuthorizationRequestQuery["mcpAuthorizationRequest"]
>;

type Props = {
  params: OAuthParams;
  csrfToken: string;
  clientName: string;
  tools: AuthorizationRequest["tools"];
  workspaces: McpAuthorizationRequestQuery["workspaces"]["items"];
  grant: MCPGrant;
};

const AuthorizePage: NextPageWithLayout<Props> = ({
  params,
  csrfToken,
  clientName,
  tools,
  workspaces,
  grant: initialGrant,
}) => {
  const { t } = useTranslation();
  const [grant, setGrant] = useState<MCPGrant>(initialGrant);
  const [isSubmitting, setSubmitting] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);
  const allowRef = useRef<HTMLInputElement>(null);
  const [authorizeConnection] = useAuthorizeMcpConnectionMutation();

  const onAccept = async () => {
    setSubmitting(true);
    const { data } = await authorizeConnection({
      variables: {
        input: {
          clientId: params.client_id ?? "",
          tools: grant.tools,
          workspaceSlugs: grant.workspaceSlugs,
        },
      },
    });
    if (!data?.authorizeMCPConnection.success) {
      setSubmitting(false);
      return;
    }
    if (allowRef.current) {
      allowRef.current.value = "True";
    }
    formRef.current?.requestSubmit();
  };

  return (
    <Page title={t("Authorize {{client}}", { client: clientName })}>
      <div className="w-full max-w-3xl">
        <div className="mb-8 flex items-center gap-4">
          <div className="relative h-10 w-28">
            <Image src={logo} layout="fill" alt="OpenHEXA" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              {t("Authorize {{client}}", { client: clientName })}
            </h1>
            <p className="text-sm text-gray-500">
              {t(
                "Choose what it may do on your behalf. You can change this at any time.",
              )}
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <MCPPermissionMatrix
            idPrefix="mcp-consent"
            grant={grant}
            workspaces={workspaces}
            tools={tools}
            onChange={setGrant}
            disabled={isSubmitting}
          />
        </div>

        <form
          ref={formRef}
          method="post"
          action={`${process.env.NEXT_PUBLIC_API_BASE_PATH ?? ""}/oauth/authorize/`}
          className="mt-6 flex items-center justify-end gap-3"
        >
          <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
          {OAUTH_FIELDS.map((field) => (
            <input
              key={field}
              type="hidden"
              name={field}
              value={params[field] ?? ""}
            />
          ))}
          <input ref={allowRef} type="hidden" name="allow" defaultValue="" />
          <Button type="submit" variant="white" disabled={isSubmitting}>
            {t("Cancel")}
          </Button>
          <Button type="button" onClick={onAccept} disabled={isSubmitting}>
            {isSubmitting && <Spinner size="xs" className="mr-1" />}
            {t("Authorize")}
          </Button>
        </form>
      </div>
    </Page>
  );
};

AuthorizePage.getLayout = (page: ReactElement) => (
  <CenteredLayout>{page}</CenteredLayout>
);

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx: GetServerSidePropsContext, client) {
    const clientId = (ctx.query.client_id as string) ?? "";
    const { data } = await client.query<McpAuthorizationRequestQuery>({
      query: McpAuthorizationRequestDocument,
      variables: { clientId, page: 1, perPage: WORKSPACES_PAGE_SIZE },
    });

    const request = data.mcpAuthorizationRequest;
    if (!request) {
      return { notFound: true };
    }

    const params: OAuthParams = {};
    for (const field of OAUTH_FIELDS) {
      const value = ctx.query[field];
      if (typeof value === "string") {
        params[field] = value;
      }
    }

    const workspaces = data.workspaces.items;
    return {
      props: {
        params,
        csrfToken: ctx.req.cookies["csrftoken"] ?? "",
        clientName: request.clientName,
        tools: request.tools,
        workspaces,
        grant: request.connection
          ? {
              tools: [...request.connection.tools],
              workspaceSlugs: request.connection.workspaces.map(
                (workspace) => workspace.slug,
              ),
            }
          : {
              tools: request.tools
                .filter((tool) => tool.resource)
                .map((tool) => tool.name),
              workspaceSlugs: workspaces.map((workspace) => workspace.slug),
            },
      },
    };
  },
});

export default AuthorizePage;
