import * as React from "react";
import { Cell } from "react-table";

export const CellContext = React.createContext<Cell | null>(null);

export function useCellContext<V = any>() {
  const cell = React.useContext(CellContext);
  if (!cell) {
    throw new Error("useCellContext muse be used inside a CellContext wrapper");
  }
  return cell as Cell<{}, V>;
}

export function CellContextProvider(props: {
  cell: Cell;
  children: React.ReactNode;
}) {
  return (
    <CellContext.Provider value={props.cell}>
      {props.children}
    </CellContext.Provider>
  );
}
