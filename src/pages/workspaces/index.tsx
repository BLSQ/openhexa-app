import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import useLocalStorage from "core/hooks/useLocalStorage";
import useMe from "identity/hooks/useMe";
import noop from "lodash/noop";
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
import { WarningAlert } from "core/components/Alert";

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!isChecking && !me.permissions.createWorkspace) {
    return (
      <WarningAlert onClose={() => router.push("/")}>
        {t("No workspace available at the moment")}
      </WarningAlert>
    );
  }
  if (typeof window === "undefined") {
    return null;
  }

  return (
    <Page title={isChecking ? "" : t("New workspace")}>
      {!isChecking ? (
        <CreateWorkspaceDialog showCancel={false} open onClose={noop} />
      ) : null}
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

    return {
      props: {
        workspaceSlug:
          data.workspaces?.items.length > 0
            ? data.workspaces.items[0]?.slug
            : null,
      },
    };
  },
});
export default WorkspacesHome;
