<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Using OpenHEXA (Legacy Version)</h1>
</div>
</div>

!!! warning "Legacy documentation"
    This page documents the legacy OpenHEXA interface. For the current platform, see the [User Manual](index.md).

## First steps

Once you or someone in your organization has gone through the [installation process](installation.md), you need to complete a few simple steps before being able to use OpenHEXA:

1. Create a team
1. Invite a few users
1. Add your first data sources

Let's go through the process.

### Creating a team

First, log-in as the root user created during the installation process.

Then, log in to OpenHEXA, and using the user dropdown menu, go to the Admin section.

<img width="600" alt="go_to_admin" src="https://user-images.githubusercontent.com/690667/192486908-08c32cdf-6f4c-4b45-ba1f-50232e8b0734.png">

You can then go to the `User management > Teams` section and add a new team :

<img width="600" alt="create_team" src="https://user-images.githubusercontent.com/690667/192489032-f8e634d9-51dd-4391-a148-89fbe53a8402.png">

You only need to provide a name for now, you will assign users to the team later on.

### Inviting users

Now that your team is created, you can invite users. Simply go to the `User management > Users` section in the admin panel and add a user :

<img width="600" alt="Screenshot 2022-09-27 at 13 04 44" src="https://user-images.githubusercontent.com/690667/192509365-90d37c52-426c-4f36-91be-bbc40799ea9e.png">

At this step, unless you really need to chose the password yourself, you should skip the password form: when you submit the user creation form, the system will send an invitation email to the user containing a link that will allow her to chose her own password.

### Adding a first datasource

Now that we have a team and a few users, let's add a datasource. We'll use the DHIS2 connector as an example, the process is almost identical for other datasources. We'll use the official [DHIS2 demo instance](https://play.dhis2.org/).

The process is as follows:

First, go to `DHIS2 connector > DHIS2 API Credentials` in the admin panel and click on `Add DHIS2 API Credentials`.

<img width="600" alt="Screenshot 2022-09-27 at 14 16 00" src="https://user-images.githubusercontent.com/690667/192524122-d15c2754-f0e2-4a47-892c-97aefd40866d.png">

After saving the credentials, go to `DHIS2 connector > DHIS2 Instances` and click on `Add DHIS2 instance`.

<img width="600" alt="Screenshot 2022-09-27 at 14 21 06" src="https://user-images.githubusercontent.com/690667/192525063-257b2fc7-69c0-4bdb-8fe0-494939fd6fa7.png">

You just need to select the API credentials created above, provide the API URL and a name for the instance. Save the form and you are done : you have added your first datasources in OpenHEXA.

You may want to add other data sources at this point, for example an AWS S3 bucket - the process is almost the same as for a DHIS2 instance, except for the credentials part.

## Using the catalog

The **data catalog** can be used to explore and search for data across your datasources.

### Exploring data

Simply go to the main OpenHEXA interface (i.e leave the admin panel if you are still there) and go to `Catalog`.

From then, you can see the list of connected datasources, and explore them in a drill-down fashion.

<img height="250" alt="Screenshot 2022-09-28 at 10 50 02" src="https://user-images.githubusercontent.com/690667/192734494-88edad37-669e-467f-9e75-737031286f3f.png">
<img height="250" alt="Screenshot 2022-09-28 at 10 50 16" src="https://user-images.githubusercontent.com/690667/192734511-a37287fc-8a3f-47a3-93bb-c8fb94d24d6c.png">

### Searching for data

To use the OpenHEXA search engine, simply click on search in the main menu or press `CMD-K`, which will open the *quick search* modal. From there, you can either:

- Enter a search term and browse the results within the search modal
- Switch to advanced search

The advanced search feature will allow you to filter your search result by content type and/or by data source.

<img height="250" alt="Screenshot 2022-09-28 at 10 52 50" src="https://user-images.githubusercontent.com/690667/192736910-edaf0d1b-5e8c-426f-b608-f8559c7d7b28.png">
<img height="250" alt="Screenshot 2022-09-28 at 10 59 53" src="https://user-images.githubusercontent.com/690667/192736931-d236d98c-4199-4213-9c82-574191465358.png">

## Using notebooks

The notebooks environment is a customized [Jupyter](https://jupyter.org/) environment.

For most of the features, you can refer to the [official Jupyterlab documentation](https://jupyterlab.readthedocs.io/en/stable/).

OpenHEXA brings a few useful additions to the standard Jupyter features:

- Mounting of S3 / GCS buckets in your Jupyter server filesystem for easier data access
- Provisioning of environment variables for the credentials of your datasources
- Pre-installation of a series of interesting Python & R libraries

Additionally, the datasource pages in the data catalog usually provide code samples illustrating how you can use the datasource in a notebook.

<img width="1326" alt="Screenshot 2022-09-28 at 12 00 24" src="https://user-images.githubusercontent.com/690667/192750757-06d597b0-d87b-477b-8053-41699a9be25c.png">

## Using data pipelines

🚧 *This section is still a work in progress*

OpenHEXA uses [Apache Airflow](https://airflow.apache.org/) to run data pipelines behind the scenes.

Before being able to use a data pipeline, you need :

- To provision an Airflow instance and to connect a Git repository for DAGs (see [installation instructions](installation.md))
- To configure a DAG Template and one or more DAGs using the admin panel in the `Airflow Connector` section
- To configure the datasources that the pipeline can access (in `Airflow Connector > Dag authorized datasources`)

One your DAG has been configured properly, you can view the corresponding pipeline in the main OpenHEXA interface and run it with the desired configuration.

<img width="600" alt="Screenshot 2022-09-28 at 12 10 48" src="https://user-images.githubusercontent.com/690667/192753050-9a305bd3-6fe7-49d8-9ecb-d52ea8d0670f.png">

<img width="600" alt="Screenshot 2022-09-28 at 12 10 57" src="https://user-images.githubusercontent.com/690667/192753093-84f1b090-6860-42c8-ad21-28778436efda.png">

