import type { CodegenConfig } from "@graphql-codegen/cli";
import { defineConfig } from "@eddeee888/gcg-operation-location-migration";

const config: CodegenConfig = {
  overwrite: true,
  schema: "../backend/**/schema.graphql",
  documents: "src/**/!(*.generated).{ts,tsx,graphql}",
  generates: {
    // "src/graphql/types.ts": {
    //   plugins: ["typescript"],
    // },
    // "src/": {
    //   preset: "near-operation-file",
    //   presetConfig: {
    //     extension: ".generated.tsx",
    //     baseTypesPath: "graphql/types.ts",
    //   },
    //   plugins: ["typescript-operations", "typescript-react-apollo"],
    //   config: {
    //     withHooks: true,
    //     scalars: {
    //       UUID: "string",
    //     },
    //   },
    // },
    // "src/graphql/possibleTypes.json": {
    //   plugins: ["fragment-matcher"],
    //   config: {
    //     module: "es2015",
    //     useExplicitTyping: true,
    //   },
    // },
    // "./schema.generated.graphql": {
    //   plugins: ["schema-ast"],
    // },
    "src/": defineConfig({
      tsConfigFilePath: "./tsconfig.json", // 👈 Path from project root to your project tsconfig.json (Note: not from the base path).
      gqlTag: {
        name: "graphql", // 👈 The tag used to parse operation documents.
        importFrom: "graphql/gql", // 👈 The the module to import the graphql tag.
        importType: "absolute", // 👈 Whether `importFrom` is relative or absolute. If relative, the path from the base path to the module.
      },
      hooksImportFrom: "@apollo/client/react", // 👈 The module to import Apollo Client hooks. Use @apollo/client for older Apollo Client v3 versions.
    }),
  },
};

export default config;
