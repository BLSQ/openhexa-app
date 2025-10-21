import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  overwrite: true,
  schema: "../backend/**/schema.graphql",
  documents: "src/**/!(*.generated).{ts,tsx,graphql}",
  generates: {
    "src/graphql/types.ts": {
      plugins: ["typescript"],
    },
    "src/": {
      preset: "near-operation-file",
      presetConfig: {
        extension: ".generated.tsx",
        baseTypesPath: "graphql/types.ts",
      },
      plugins: ["typescript-operations", "typescript-react-apollo"],
      config: {
        withHooks: true,
        scalars: {
          UUID: "string",
        },
      },
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
