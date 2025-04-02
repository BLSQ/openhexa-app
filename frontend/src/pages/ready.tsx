import { NextPageWithLayout } from "core/helpers/types";

const ReadyPage: NextPageWithLayout = () => {
  return <span>ok</span>;
};

ReadyPage.getLayout = (page) => page;

export default ReadyPage;
