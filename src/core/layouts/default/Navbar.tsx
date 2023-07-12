import Link from "core/components/Link";
import useFeature from "identity/hooks/useFeature";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { ReactNode } from "react";

const Classes = {
  item: "px-3 py-2 rounded-md hover:bg-gray-700 hover:text-white text-gray-300",
  activeItem:
    "px-3 py-2 rounded-md hover:bg-gray-700 hover:text-white bg-gray-900 text-white",
};

const Item = ({ href, children }: { href: string; children: ReactNode }) => {
  const router = useRouter();
  return (
    <Link
      href={href}
      customStyle={router.asPath === href ? Classes.activeItem : Classes.item}
    >
      {children}
    </Link>
  );
};

const Navbar = () => {
  const { t } = useTranslation();
  return (
    <nav className="relative flex flex-1 items-center space-x-4 text-sm font-medium">
      <Item href="/">{t("Dashboard")}</Item>
      <Item href="/catalog">{t("Catalog")}</Item>
      <Item href="/notebooks">{t("Notebooks")}</Item>
      <Item href="/pipelines">{t("Pipelines")}</Item>
      <Item href="/visualizations">{t("Visualizations")}</Item>
    </nav>
  );
};

export default Navbar;
