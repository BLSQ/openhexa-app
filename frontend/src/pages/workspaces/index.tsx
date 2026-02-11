import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { usePublicEnv } from "core/helpers/runtimeConfig";
import useLocalStorage from "core/hooks/useLocalStorage";
import useMe from "identity/hooks/useMe";
import { useRouter } from "next/router";
import { ReactElement, useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import CreateWorkspaceDialog from "workspaces/features/CreateWorkspaceDialog";
import {
  WorkspacesPageDocument,
  WorkspacesPageQuery,
  WorkspacesPageQueryVariables,
  useCheckWorkspaceAvailabilityLazyQuery,
} from "workspaces/graphql/queries.generated";
import NoWorkspaceLayout from "workspaces/layouts/NoWorkspaceLayout";
import {
  ArrowTopRightOnSquareIcon,
  InboxIcon,
} from "@heroicons/react/24/outline";
import Link from "core/components/Link";
import {
  OrganizationsDocument,
  OrganizationsQuery,
} from "organizations/graphql/queries.generated";

type WorkspacesHomeProps = {
  workspaceSlug: string | null;
};

const WorkspacesHome = (props: WorkspacesHomeProps) => {
  const { t } = useTranslation();
  const me = useMe();
  const router = useRouter();
  const [check] = useCheckWorkspaceAvailabilityLazyQuery();

  const [lastWorkspace, setLastWorkspace] = useLocalStorage(
    "last-visited-workspace",
  );
  const [isChecking, setChecking] = useState(true);
  const [isDialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    if (!isChecking || typeof window === "undefined") return;
    const promise = lastWorkspace
      ? check({ variables: { slug: lastWorkspace } }).then(
          (res) => res.data?.workspace,
        )
      : Promise.resolve(null);

    promise.then((workspace) => {
      if (workspace) {
        // We have a workspace matching the last visited one, redirect to it
        router.replace(`/workspaces/${workspace.slug}`);
      } else if (props.workspaceSlug) {
        // We don't have a workspace matching the last visited one, but we have
        // a workspace to redirect to, so we do it
        setLastWorkspace(null);
        router.push(`/workspaces/${props.workspaceSlug}`);
      } else {
        // Let's propose the user to create a new workspace
        setChecking(false);
      }
    });
  }, []);

  const { CONSOLE_URL } = usePublicEnv();

  if (typeof window === "undefined" || isChecking) {
    return null;
  }

  return (
    <Page title={t("Workspaces")}>
      <NoWorkspaceLayout>
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <InboxIcon className="h-12 w-12 text-gray-400 mb-4" />
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            {t("No workspace available")}
          </h2>
          <p className="text-sm text-gray-500 max-w-md">
            {t("You don't have access to any workspace yet.")}
          </p>
          <p className="text-sm text-gray-500 max-w-md mt-2">
            {t(
              "Contact your administrator or a member of the OpenHEXA team to get invited to a workspace.",
            )}
          </p>
          {CONSOLE_URL && (
            <Link
              href={CONSOLE_URL}
              target="_blank"
              noStyle
              className="mt-6 inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
            >
              {t("Or create your own organization")}
              <ArrowTopRightOnSquareIcon className="h-4 w-4" />
            </Link>
          )}
          {me.permissions.createWorkspace && (
            <button
              onClick={() => setDialogOpen(true)}
              className="mt-6 inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500"
            >
              {t("Create a workspace")}
            </button>
          )}
        </div>
        {me.permissions.createWorkspace && (
          <CreateWorkspaceDialog
            open={isDialogOpen}
            onClose={() => setDialogOpen(false)}
          />
        )}
      </NoWorkspaceLayout>
    </Page>
  );
};

WorkspacesHome.getLayout = (page: ReactElement) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query<
      WorkspacesPageQuery,
      WorkspacesPageQueryVariables
    >({
      query: WorkspacesPageDocument,
    });

    const hasWorkspaces = (data.workspaces?.items.length ?? 0) > 0;

    if (!hasWorkspaces) {
      const { data: orgData } = await client.query<OrganizationsQuery>({
        query: OrganizationsDocument,
      });

      const organizations = orgData.organizations ?? [];

      if (organizations.length === 1) {
        return {
          redirect: {
            destination: `/organizations/${organizations[0].id}`,
            permanent: false,
          },
        };
      } else if (organizations.length > 1) {
        return {
          redirect: {
            destination: "/organizations",
            permanent: false,
          },
        };
      }
    }

    return {
      props: {
        workspaceSlug: hasWorkspaces ? data.workspaces.items[0]?.slug : null,
      },
    };
  },
});
export default WorkspacesHome;
