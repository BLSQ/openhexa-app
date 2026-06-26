import Spinner from "core/components/Spinner";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "next-i18next";

const ROTATE_INTERVAL_MS = 3500;
const DOT_INTERVAL_MS = 400;

// Pick a random index, optionally avoiding the current one so the verb always
// visibly changes when it rotates.
function pickIndex(length: number, exclude?: number): number {
  if (length <= 1) return 0;
  const span = exclude === undefined ? length : length - 1;
  const idx = Math.floor(Math.random() * span);
  return exclude === undefined || idx < exclude ? idx : idx + 1;
}

export default function ThinkingIndicator() {
  const { t } = useTranslation();

  const verbs = useMemo(
    () => [
      t("Thinking"),
      t("Working on it"),
      t("Pondering"),
      t("Analyzing"),
      t("Reasoning"),
      t("Processing"),
    ],
    [t],
  );

  const [index, setIndex] = useState(() => pickIndex(verbs.length));
  const [dotCount, setDotCount] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setIndex((prev) => pickIndex(verbs.length, prev));
    }, ROTATE_INTERVAL_MS);
    return () => clearInterval(id);
  }, [verbs.length]);

  useEffect(() => {
    const id = setInterval(() => {
      setDotCount((count) => (count + 1) % 4);
    }, DOT_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-2 rounded-2xl bg-gray-100 px-4 py-3 text-sm">
        <Spinner size="xs" className="text-gray-400" />
        <span className="font-medium italic text-gray-500">
          {verbs[index]}
          {/* Fixed width so the bubble doesn't jitter as the dots cycle. */}
          <span className="inline-block w-4 text-left align-bottom">
            {".".repeat(dotCount)}
          </span>
        </span>
      </div>
    </div>
  );
}
