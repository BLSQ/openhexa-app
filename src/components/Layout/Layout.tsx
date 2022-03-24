import { CustomApolloClient } from "libs/apollo";
import type { ReactElement } from "react";
import Footer from "./Footer";
import Header from "./Header";

type LayoutProps = {
  children: ReactElement;
  pageProps: any;
  header?: ReactElement | null;
};

const Layout = (props: LayoutProps) => {
  const { children, pageProps } = props;
  return (
    <div className="min-h-screen flex flex-col ">
      {pageProps.user && <Header />}
      {children}
      <Footer />
    </div>
  );
};

Layout.prefetch = async (client: CustomApolloClient) => {
  await Header.prefetch(client);
};

export default Layout;
