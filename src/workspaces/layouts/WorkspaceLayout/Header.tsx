import clsx from "clsx";
import Avatar from "core/components/Avatar";
import Menu from "core/components/Menu";
import { logout } from "identity/helpers/auth";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { ReactNode } from "react";
import { WORKSPACES } from "workspaces/helpers/fixtures";

type HeaderProps = {
  children?: ReactNode;
};

const Header = (props: HeaderProps) => {
  const me = useMe();
  const router = useRouter();
  const { t } = useTranslation();
  return (
    <div
      className={clsx(
        "sticky top-0 z-10 flex h-16 flex-shrink-0 items-center justify-between border-b border-gray-200 bg-white py-3 shadow",
        "px-4 md:px-6 xl:px-10 2xl:px-12"
      )}
    >
      <div className="flex-1">{props.children}</div>
      <Menu
        trigger={
          <Avatar
            initials={me.user?.avatar.initials ?? ""}
            color={me.user ? me.user.avatar.color : undefined}
            size="sm"
          />
        }
      >
        <Menu.Item onClick={() => router.push("/user/account")}>
          {t("Your account")}
        </Menu.Item>
        <Menu.Item
          onClick={() =>
            router.push({
              pathname: "/workspaces/[workspaceId]",
              query: { workspaceId: WORKSPACES[0].id },
            })
          }
        >
          {t("Your workspaces")}
        </Menu.Item>
        {me.permissions.adminPanel && (
          <Menu.Item onClick={() => router.push("/admin")}>
            {t("Administration")}
          </Menu.Item>
        )}

        <Menu.Item onClick={() => logout()}>{t("Sign out")}</Menu.Item>
      </Menu>
    </div>
  );
};

export default Header;
