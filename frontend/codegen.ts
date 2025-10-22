import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  overwrite: true,
  schema: "../backend/**/schema.graphql",
  documents: "src/**/!(*.generated).{ts,tsx,graphql}",
  generates: {
    "src/graphql/types.ts": {
      plugins: ["typescript"],
    },
    "src/graphql/": {
      preset: "client",
    },
    "src/graphql/possibleTypes.json": {
      plugins: ["fragment-matcher"],
      config: {
        module: "es2015",
        useExplicitTyping: true,
      },
    },
    "./schema.generated.graphql": {
      plugins: ["schema-ast"],
    },
  },
};

export default config;
