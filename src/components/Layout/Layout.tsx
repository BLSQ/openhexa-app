import { gql } from "@apollo/client";
import { CustomApolloClient } from "libs/apollo";
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
      {pageProps.user && <Header user={pageProps.user} />}
      {children}
    </div>
  );
};

Layout.prefetch = async (client: CustomApolloClient) => {};

export default Layout;
