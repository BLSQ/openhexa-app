import { useMemo } from "react";
import useMe from "./useMe";

type UseFeatureResult = [isEnabled: boolean];

export default function useFeature(code: string): UseFeatureResult {
  const me = useMe();

  const feature = useMemo(
    () => me.features.find((x) => x.code === code),
    [me, code],
  );

  return [Boolean(feature)];
}
