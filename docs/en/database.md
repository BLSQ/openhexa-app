<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Database</h1>
</div>
</div>
Every workspace has a dedicated PostgreSQL relational database. You can use this database to store structured (relational) data for your workspace. You can easily access it from external visualization solutions such as Tableau or Power BI.

## Features

All workspace members can browse database tables and preview data in each table. However, access to database credentials and write permissions depend on your role:

!!! info "Database permissions by role"
    - **Viewers**: Can browse tables and view data, but cannot see database credentials or write to the database
    - **Editors**: Can browse tables, view data, access database credentials, and write to the database
    - **Admins**: Can browse tables, view data, access database credentials, write to the database, and regenerate the database password

![Database Interface](../assets/images/database/database.png)

You can use the workspace database in OpenHEXA notebooks and OpenHEXA data pipelines.

You can also use your OpenHEXA workspace database as a data source in data visualization and BI tools like Tableau or Power BI. Simply copy the connection parameters from the database page and paste them into your tool.

## Connect to Apache Superset

Apache Superset is a popular open-source data visualization and exploration platform. You can connect your OpenHEXA workspace database to Superset for advanced analytics and dashboard creation.


1. **Access database connection parameters**
    - Go to your workspace database page in OpenHEXA.
    - Copy the connection parameters (host, port, database name, username, and password).

2. **Add database in Superset**
    - In Superset, go to **Settings** > **Database Connections**.
    - Click **+ Database** to add a new connection.
    - Select **PostgreSQL** as the database type.

3. **Configure connection**
    - **Host**: The host from your OpenHEXA database parameters
    - **Port**: The port from your OpenHEXA database parameters
    - **Database Name**: The database name from your workspace
    - **Username**: The provided username
    - **Password**: The provided password
    - **Display Name**: A descriptive name for your connection (for example, "OpenHEXA Workspace DB")

4. **Test and save**
    - Click **Test Connection** to verify the setup.
    - If successful, click **Connect** to save the database connection.

