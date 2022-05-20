import dynamic from "next/dynamic";
import { useRouter } from "next/router";

const PluginPage = () => {
  const router = useRouter();
  if (!router.query.plugin) return null;

  const Page = dynamic(
    () => import(`../plugins/${router.query?.plugin as string}`)
  );
  return (
    <div>
      <Page />
    </div>
  );
};

export default PluginPage;
