import { CustomApolloClient } from "core/helpers/apollo";
import useMe from "identity/hooks/useMe";
import type { ReactElement } from "react";
import Header from "./Header";
import PageContent from "./PageContent";

type LayoutProps = {
  children: ReactElement;
  pageProps: any;
};

const Layout = (props: LayoutProps) => {
  const { children } = props;
  const me = useMe();
  return (
    <div className="flex min-h-screen flex-col ">
      <Header />
      {children}
    </div>
  );
};

Layout.PageContent = PageContent;

Layout.prefetch = async (client: CustomApolloClient) => {};

export default Layout;
