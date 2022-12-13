import { Faker, faker } from "@faker-js/faker";
import { DagRunStatus, DagRunTrigger } from "graphql-types";
import { DateTime } from "luxon";

faker.seed(0);

const SAMPLE_PROJECTS = [
  "CMR PNLP",
  "BFA Malaria Data Repository",
  "SEN Master Facility List",
  "NER Malaria Risk Modelling",
  "COD Accessibility to Health Services",
];

function searchForFile(files: any, searchId: any) {
  for (const f of files) {
    if (f.id === searchId) return f;
    if (f.type === "folder") {
      let found: any = searchForFile(f.children, searchId);
      if (found) return found;
    }
  }
}

export const getWorkspaceFile = (workspaceId: any, fileId: any) => {
  const workspace = WORKSPACES.find(
    (workspace) => workspace.id === workspaceId
  );

  if (!workspace) return null;

  return searchForFile(workspace.files, fileId);
};

export const WORKSPACES = SAMPLE_PROJECTS.map((project, i) => ({
  id: faker.datatype.uuid(),
  name: project,
  country:
    i % 3 === 0
      ? null
      : {
          code: faker.address.countryCode().toLowerCase(),
        },
  description: `# Malaria Data Repository for Cameroon


  Welcome to the Cameroon Malaria Data Repository workspace !
  
  
  This workspace contains :
  
  
  - The data produced by Bluesquare in the context of this project
  - The different notebooks used for exploration and visualisation purposes
  - The data pipelines that we use to process the Malaria Data
  
  
  ## Quick links
  
  
  - [Annex A reports → lien vers le dossier](https://google.com)
  - [Link to pipeline ](https://google.com)
  
  
  ## Overview of the data in the repository
  
  
  Nunc fringilla, nisi eu hendrerit ornare, lacus massa accumsan eros, quis auctor nibh lorem sed ligula. Praesent ac rhoncus mi. Cras fermentum ultrices pellentesque. Maecenas odio ex, euismod sit amet odio ut, tristique cursus massa. 
  
  
  Nam congue mi eu metus sagittis rutrum sit amet suscipit nisi. Donec a consectetur orci, nec tempus dui. Proin tristique ex nec magna porttitor feugiat ut vel est. Pellentesque feugiat aliquet augue. Pellentesque a risus id dolor interdum convallis. Suspendisse condimentum in diam tempus dapibus. Mauris blandit dolor non felis dignissim, et tincidunt justo efficitur.
  
  
  `,
  files: [
    {
      type: "folder",
      name: "Output",
      id: faker.datatype.uuid(),
      updatedAt: faker.datatype
        .datetime({
          min: DateTime.now().minus({ days: 28 }).toMillis(),
          max: DateTime.now().toMillis(),
        })
        .toISOString(),
      children: Array.from({ length: 13 }, () => ({
        id: faker.datatype.uuid(),
        name: faker.system.fileName(),
        type: faker.system.fileType(),
        size: faker.datatype.number(1000 * 10 * 10 * 10),
        updatedAt: faker.datatype
          .datetime({
            min: DateTime.now().minus({ days: 28 }).toMillis(),
            max: DateTime.now().toMillis(),
          })
          .toISOString(),
      })),
    },
    {
      type: "markdown",
      id: faker.datatype.uuid(),
      name: "README.md",
      size: faker.datatype.number(1000 * 10 * 10 * 10),
      updatedAt: faker.datatype
        .datetime({
          min: DateTime.now().minus({ days: 28 }).toMillis(),
          max: DateTime.now().toMillis(),
        })
        .toISOString(),
    },
  ],

  database: {
    workspaceTables: Array.from({ length: 10 }, () => ({
      id: faker.datatype.uuid(),
      name: faker.science.chemicalElement().name,
      description: faker.lorem.paragraph(2),
      schema: Array.from({ length: 4 }, () => ({
        fieldName: faker.database.column(),
        type: faker.database.type(),
        sample: faker.hacker.noun(),
      })),
      content: faker.datatype.number(),
      createdAt: faker.datatype
        .datetime({
          min: DateTime.now().minus({ days: 28 }).toMillis(),
          max: DateTime.now().toMillis(),
        })
        .toISOString(),
      codeSample: [
        `
        import os
        import pandas as pd
        from sqlalchemy import create_engine
        
        engine = create_engine(os.environ["POSTGRESQL_HEXA_EXPLORE_DEMO_URL"])
        
        # Create sample dataframe
        df = pd.DataFrame({"name": ["Jane", "John", "Tyler"], "age": [19, 17, 22]})
        
        # Write data
        df.to_sql("database_tutorial", con=engine, if_exists="replace")
        
        # Read data
        pd.read_sql("SELECT * FROM database_tutorial", con=engine)
        `,
        `
        library(DBI)

        con <- dbConnect(
            RPostgres::Postgres(),
            dbname = Sys.getenv("POSTGRESQL_HEXA_EXPLORE_DEMO_DATABASE"),
            host = Sys.getenv("POSTGRESQL_HEXA_EXPLORE_DEMO_HOSTNAME"),
            port = Sys.getenv("POSTGRESQL_HEXA_EXPLORE_DEMO_PORT"),
            user = Sys.getenv("POSTGRESQL_HEXA_EXPLORE_DEMO_USERNAME"),
            password = Sys.getenv("POSTGRESQL_HEXA_EXPLORE_DEMO_PASSWORD")
        )
        
        dbWriteTable(con, "some_table_name", Data_fin, overwrite=TRUE)
        `,
      ],
    })),
  },
  dags: Array.from({ length: 4 }, () => ({
    id: faker.datatype.uuid(),
    label: faker.science.chemicalElement().name,
    formCode: faker.helpers.arrayElement(["papermill", "ihp"]),
    externalUrl: "https://airflow.demo.openhexa.org/graph?dag_id=ihp-update",
    template: {
      sampleConfig: faker.lorem.paragraph(2),
      code: faker.helpers.arrayElement(["papermill", "ihp"]),
    },
    description: `
Compute an accessibility analysis for a given set of tile, barrier information, walk speed etc

#### Parameter reference

Paths:

- \`output-dir\`: a valid S3 path to put the result
- \`health-facilities\`: a valid s3 path to put the destination point layer
- \`dem\`: a valid s3 path to download the DEM
- \`slope\`: a valid s3 path to download the slope raster
- \`land-cover\`: a valid s3 path to download the landcover raster
- \`transport-network\`: a valid s3 path to download the transport network layer
- \`barrier\`: a valid s3 path to download the barrier layer
- \`water\`: a valid s3 path to download the  water layer
- \`moving-speeds\`: a valid s3 path to download the scenario file
`,
    externalId: faker.word.noun({
      length: { min: 15, max: 30 },
      strategy: "longest",
    }),
    config:
      'curl -d "param1=value1&param2=value2" -X POST -H "Authorization: Bearer mytoken123" http://api.openhexa.org/workspaces/12fe/pipelines/32gf',
    runs: [
      {
        id: faker.datatype.uuid(),
        externalId: "Manual",
        isFavorite: faker.datatype.boolean(),
        progress: faker.datatype.float(),
        triggerMode: faker.helpers.arrayElement(Object.values(DagRunTrigger)),
        status: faker.helpers.arrayElement(Object.values(DagRunStatus)),
        executionDate: faker.datatype
          .datetime({
            min: DateTime.now().minus({ days: 28 }).toMillis(),
            max: DateTime.now().toMillis(),
          })
          .toISOString(),
        duration: faker.datatype.number(),
        outputs: Array.from({ length: 2 }, () => ({
          title: faker.system.fileName(),
          uri: faker.internet.url(),
        })),
        logs: faker.lorem.paragraph(20),
        config: {
          parameters: {
            country: "be",
            quarter: "2020-01",
          },
          in_notebook: "s3://hexa-bucket/project/notebook.ipynb",
          limit_memory: "2000M",
          out_notebook:
            "s3://hexa-bucket/project/output/2020-01-01_notebook_output.ipynb",
          request_memory: "1500M",
        },
        messages: Array.from({ length: 2 }, () => ({
          message: faker.lorem.sentence(1),

          priority: faker.helpers.arrayElement(["INFO", "ERROR", "WARNING"]),
        })),
      },
    ],
  })),
  notebooksUrl: faker.internet.url(),
  members: Array.from({ length: 5 }, () => ({
    name: faker.name.fullName(),
    email: faker.internet.email(),
    role: faker.word.noun({
      length: { min: 15, max: 30 },
      strategy: "longest",
    }),
    createdAt: faker.datatype
      .datetime({
        min: DateTime.now().minus({ days: 28 }).toMillis(),
        max: DateTime.now().toMillis(),
      })
      .toISOString(),
  })),
  connections: Array.from({ length: 7 }, () => ({
    id: faker.datatype.uuid(),
    name: faker.word.noun({
      length: { min: 15, max: 30 },
      strategy: "longest",
    }),
    description: faker.lorem.paragraph(1),
    type: [
      { label: "DHIS2", color: "bg-teal-100 text-teal-400", value: "dhis2" },
      {
        label: "PostgreSQL",
        color: "bg-blue-50 text-blue-400",
        value: "postgresql",
      },
      {
        label: "S3 Bucket",
        color: "bg-orange-100 text-orange-400",
        value: "aws_s3_bucket",
      },
      {
        label: "GCS Bucket",
        color: "bg-sky-100 text-sky-500",
        value: "gcs_bucket",
      },
      { label: "Custom", color: "bg-gray-50 text-gray-300", value: "" },
    ][faker.datatype.number(3)],
    owner: faker.company.name(),
    credentials: [
      {
        label: "url",
        value: faker.internet.url(),
        secret: false,
      },
      {
        label: "username",
        value: faker.internet.userName(),
        secret: false,
      },
      {
        label: "password",
        value: faker.internet.password(),
        secret: true,
      },
    ],
  })),
}));
