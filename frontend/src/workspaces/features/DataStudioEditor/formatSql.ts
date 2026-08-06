import { format } from "sql-formatter";

// Workspace databases are PostgreSQL, so parse with its dialect: the ANSI
// dialect chokes on Postgres-only syntax (casts with `::`, `RETURNING`, …).
const OPTIONS = {
  language: "postgresql",
  keywordCase: "upper",
  tabWidth: 2,
} as const;

/**
 * Pretty-print a SQL query. A query that cannot be parsed — which is the normal
 * state of a half-typed one — is returned untouched rather than mangled, so
 * formatting is never destructive.
 */
export const formatSql = (sql: string): string => {
  try {
    return format(sql, OPTIONS);
  } catch {
    return sql;
  }
};
