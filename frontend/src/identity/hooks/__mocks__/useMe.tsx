import { ReactNode } from "react";

export function MeProvider(props: { me?: string; children: ReactNode }) {
  return props.children;
}

export default jest.fn();
