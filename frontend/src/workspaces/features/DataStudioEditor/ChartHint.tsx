import { ChartBarIcon } from "@heroicons/react/24/outline";
import Tooltip from "core/components/Tooltip";
import { useTranslation } from "next-i18next";
import { SQL_WIDGETS_DOCS_URL } from "workspaces/helpers/dataStudio";
import { ChartKind, CHART_CONVENTIONS } from "./chart";

const ChartHint = () => {
  const { t } = useTranslation();

  // The same keys the charts use for their own accessible names, so a chart type
  // is not named two different ways in two places.
  const kindLabels: Record<ChartKind, string> = {
    bar: t("Bar chart"),
    line: t("Line chart"),
    pie: t("Pie chart"),
  };

  return (
    <Tooltip
      placement="top"
      label={
        <div className="break-normal">
          <p className="mb-1.5 font-medium text-gray-700">
            {t("Turn a result into a chart")}
          </p>
          <p className="mb-1.5">
            {t(
              "Alias two columns to one of these pairs and the result is drawn as a chart, with the table one tab away:",
            )}
          </p>
          <ul className="space-y-0.5">
            {CHART_CONVENTIONS.map((convention) => (
              <li
                key={convention.kind}
                className="flex items-baseline justify-between gap-4 whitespace-nowrap"
              >
                <span className="font-mono text-gray-700">
                  {convention.label}, {convention.value}
                </span>
                <span className="text-gray-400">
                  {kindLabels[convention.kind]}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-1.5 text-gray-400">
            {t("Click to read the guide.")}
          </p>
        </div>
      }
      renderTrigger={(ref) => (
        // The trigger is itself the link to the guide, so the tooltip never has
        // to be made interactive for the user to reach the documentation.
        <span ref={ref}>
          <a
            href={SQL_WIDGETS_DOCS_URL}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 text-blue-600 hover:text-blue-500"
          >
            <ChartBarIcon className="h-3.5 w-3.5 shrink-0" />
            {t("Chart this result")}
          </a>
        </span>
      )}
    />
  );
};

export default ChartHint;
