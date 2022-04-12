import { NextPageWithLayout } from "libs/types";

const ReadyPage: NextPageWithLayout = () => {
  return <span>ok</span>;
};

ReadyPage.getLayout = (page) => page;

export default ReadyPage;
