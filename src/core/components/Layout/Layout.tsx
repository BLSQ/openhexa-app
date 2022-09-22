import { CustomApolloClient } from "core/helpers/apollo";
import type { ReactElement } from "react";
import Header from "./Header";

type LayoutProps = {
  children: ReactElement;
  pageProps: any;
};

const Layout = (props: LayoutProps) => {
  const { children, pageProps } = props;
  return (
    <div className="flex min-h-screen flex-col ">
      {pageProps.me && <Header me={pageProps.me} />}
      {children}
    </div>
  );
};

Layout.prefetch = async (client: CustomApolloClient) => {};

export default Layout;
