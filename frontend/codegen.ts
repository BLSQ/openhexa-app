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
      presetConfig: {
        baseTypesPath: "graphql/types.ts",
      },
      config: {
        withHooks: true,
        scalars: {
          UUID: "string",
        },
      },
    },
    "./schema.generated.graphql": {
      plugins: ["schema-ast"],
    },
  },
};

export default config;
