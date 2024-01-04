import Head from "next/head";
import { ReactNode, useMemo } from "react";

type Props = {
  children: ReactNode;
  title?: string;
};

const Page = (props: Props) => {
  const { children, title } = props;

  const pageTitle = useMemo(() => {
    return title ? `OpenHEXA | ${title}` : "OpenHEXA";
  }, [title]);

  return (
    <>
      <Head>
        <title key="title">{pageTitle}</title>
        <meta property="og:title" content={pageTitle} key="meta_title" />
      </Head>
      {children}
    </>
  );
};

export default Page;
