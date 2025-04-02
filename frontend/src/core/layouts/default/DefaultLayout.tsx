import { CustomApolloClient } from "core/helpers/apollo";
import type { ReactElement } from "react";
import PageContent from "./PageContent";

type LayoutProps = {
  children: ReactElement;
  pageProps: any;
};

const Layout = (props: LayoutProps) => {
  const { children } = props;
  return <div className="flex min-h-screen flex-col ">{children}</div>;
};

Layout.PageContent = PageContent;

Layout.prefetch = async (client: CustomApolloClient) => {};

export default Layout;
