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

export const WORKSPACES = SAMPLE_PROJECTS.map((project) => ({
  id: faker.datatype.uuid(),
  name: project,
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
  files: Array.from({ length: 13 }, () => ({
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
  sharedFiles: Array.from({ length: 4 }, () => ({
    id: faker.datatype.uuid(),
    name: faker.system.fileName(),
    type: faker.system.fileType(),
    size: faker.datatype.number(1000 * 10 * 10 * 10),
    origin: faker.company.name(),
    updatedAt: faker.datatype
      .datetime({
        min: DateTime.now().minus({ days: 28 }).toMillis(),
        max: DateTime.now().toMillis(),
      })
      .toISOString(),
  })),
  database: {
    workspaceTables: Array.from({ length: 10 }, () => ({
      id: faker.datatype.uuid(),
      name: faker.word.noun({
        length: { min: 15, max: 30 },
        strategy: "longest",
      }),
      description: faker.lorem.paragraph(2),
      schema: Array.from({ length: 4 }, () => ({
        fieldName: faker.database.column(),
        type: faker.database.type(),
        sample: faker.hacker.noun(),
      })),
      content: faker.datatype.number(),
      updatedAt: faker.datatype
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
    sharedTables: Array.from({ length: 4 }, () => ({
      id: faker.datatype.uuid(),
      name: faker.word.noun({
        length: { min: 15, max: 30 },
        strategy: "longest",
      }),
      description: faker.lorem.paragraph(2),
      schema: Array.from({ length: 4 }, () => ({
        fieldName: faker.database.column(),
        type: faker.database.type(),
        sample: faker.hacker.noun(),
      })),
      content: faker.datatype.number(),
      updatedAt: faker.datatype
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
    label: faker.word.noun({
      length: { min: 15, max: 30 },
      strategy: "longest",
    }),
    description: faker.lorem.paragraph(4),
    externalId: faker.word.noun({
      length: { min: 15, max: 30 },
      strategy: "longest",
    }),
    config:
      'curl -d "param1=value1&param2=value2" -X POST -H "Authorization: Bearer mytoken123" http://api.openhexa.org/workspaces/12fe/pipelines/32gf',
    runs: [
      {
        id: faker.datatype.uuid(),
        triggerMode: faker.helpers.arrayElement(Object.values(DagRunTrigger)),
        status: faker.helpers.arrayElement(Object.values(DagRunStatus)),
        executionDate: faker.datatype
          .datetime({
            min: DateTime.now().minus({ days: 28 }).toMillis(),
            max: DateTime.now().toMillis(),
          })
          .toISOString(),
        duration: faker.datatype.bigInt(),
        output: Array.from({ length: 2 }, () => ({
          title: faker.system.fileName(),
          uri: faker.internet.url(),
        })),
        logs: faker.lorem.paragraph(10),
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
  connections: Array.from({ length: 3 }, () => ({
    id: faker.datatype.uuid(),
    name: faker.word.noun({
      length: { min: 15, max: 30 },
      strategy: "longest",
    }),
    description: faker.lorem.paragraph(4),
    type: faker.helpers.arrayElement(["DHSI2", "PostgreSQL", "GCP"]),
    owner: faker.company.name(),
    credentials: {
      url: faker.internet.url(),
      username: faker.internet.userName(),
      password: faker.internet.password(),
    },
  })),
}));
