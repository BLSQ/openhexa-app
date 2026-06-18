import clsx from "clsx";
import { useMemo, useState } from "react";
import { columnsOf, formatCell, Row } from "./tabular";

export default function TableValue({ rows }: { rows: Row[] }) {
  const columns = useMemo(() => columnsOf(rows), [rows]);
  // Cells are truncated for scannability; clicking one expands it in place so
  // large values (long descriptions, content blobs) stay readable.
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  return (
    <div className="overflow-x-auto rounded-md border border-gray-200 pb-1.5">
      <table className="min-w-full border-collapse text-xs">
        <thead className="bg-gray-50 text-gray-500">
          <tr>
            {columns.map((col) => (
              <th
                key={col}
                className="whitespace-nowrap px-2.5 py-1.5 text-left font-medium"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.map((row, i) => (
            <tr key={i} className="even:bg-gray-50/40">
              {columns.map((col) => {
                const key = `${i}:${col}`;
                const text = formatCell(row[col]);
                const isOpen = expanded[key];
                return (
                  <td
                    key={col}
                    title={isOpen ? undefined : text}
                    onClick={() =>
                      setExpanded((e) => ({ ...e, [key]: !e[key] }))
                    }
                    className={clsx(
                      "cursor-pointer px-2.5 py-1.5 align-top font-mono text-gray-700",
                      isOpen
                        ? "whitespace-pre-wrap break-words"
                        : "max-w-[16rem] truncate",
                    )}
                  >
                    {text}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
