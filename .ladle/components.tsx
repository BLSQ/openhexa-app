import React from "react";
import type { GlobalProvider } from "@ladle/react";
import "styles/globals.css";
import "./styles.css";

export const Provider: GlobalProvider = ({ children }) => (
  <div className="border-2 border-dotted border-gray-300">{children}</div>
);
