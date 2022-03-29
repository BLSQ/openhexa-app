Changelog
=========

Version 0.30
------------

March 29, 2022

### Updated

- Revamped permission/access control for data sources and pipelines
- Enforce trailing slashes for all URLs to prepare the next frontend iteration

### Fixed

- Fixed Airflow cluster external link

Version 0.29
------------

March 24, 2022

### Updated

- Enforce S3 permission restriction for pipeline
- Inject datasource information into notebooks and pipelines, the same way

### Fixed

- Fixing horizontal scroll issues
- Removed Extract model and features in DHIS2 module

Version 0.28
------------

March 14, 2022

### Added

- User can add pipeline runs to favorites to easily retrieve them later and relaunch them

### Updated

- Collect and show pipeline run durations
- DHIS2 credentials injection in notebooks

Version 0.27
------------

March 8, 2022

### Fixed

- Fixed horizontal scrolling issues in grids
- Fixed crash in DAGRun admin list view

Version 0.26
------------

March 1, 2022

### Updated

- Refresh worker to keep the state of each Airflow DAGRun up to date faster
- Airflow pipeline sync is faster if there is no need to recompute DAGs

Version 0.25
------------

February 22, 2022

### Updated

- Data model for connector_airflow, to better reflect the way the DAG works
- Locale management for DHIS2, add a preference to english locales when syncing an instance
- DHIS2 sync deletes openhexa objects if they disapear on the remote instance

Version 0.24
------------

February 15, 2022

### Added

- Added dev container for GitHub workspaces

### Updated

- Updated to Django 4.0.2

Version 0.23
------------

February 8, 2022

### Added

- Support DAG template for connector_airflow
- User can edit DAG name, schedule and owner themself

Version 0.22
------------

February 1, 2022

### Fixed

- Fixed fixtures command in Docker entrypoint

Version 0.21
------------

January 25, 2022

### Updated

- Improved grids UX (should fix horizontal scrolling issues) 
- Improved search UX (no results if no query, handling of long text)

### Fixed

- Fixed bug with truncated search query when switching from quick to advanced search

Version 0.20
------------

January 18, 2022

### Updated

- Updated project dependencies (fixed vulnerabilities)
- Hardened security settings

### Fixed

- Fixed last_synced_at on DHIS2 content

Version 0.19
------------

January 11, 2022

### Added

- Added the foundations of the OpenHexa GraphQL API
- Implemented Auth GraphQL API

### Updated

- Treat user emails (and thus login) in a case-insensitive way

### Fixed

- Fixed issue in IndicatorType admin

Version 0.18
------------

January 4, 2022

### Updated

- Removed the notion of orphans from S3 data model
- Simplified S3 sync

### Fixed

- Fixed regression on invite user with admin
- Fixed the search by id for DHIS2
- Fixed permission issue in Pipelines
- Fixed issue with duplicate indicator types across instances

Version 0.17
------------

December 28, 2021

### Added

- Added "Open in Airflow" button for superusers (allows superusers to view DAGs / DAG runs in Airflow)

### Updated

- Display more explicitly the underlying DAG in DAG run detail screens 
- Added the possibility to force-activate features (activate it for all users without regard to their specific flags)
- Updated to Django 4.x (and other Python dependency updates)
- Added datasource name in quick search results

### Fixed

- Fixed issue with pagination on DAG detail page
- Fixed sync issue related to DHIS2 objects with the same id
- Fixed tailwind watch issue

Version 0.16
------------

December 21, 2021

### Updated

- Added Coverage analysis in build pipeline
- Replaced s3fs by boto
- More logs for the DHIS2 connector

### Fixed

- Fixed issue with S3 objects whose key start by a slash (`/`)
- Fixed issue with search queries containing a column (`:`)
- Fixed issue with search queries containing an invalid type filter
- Fixed issue with search queries containing only filters or exact words

Version 0.15
------------

December 14, 2021

### Added

- New search interface, with filters for data sources and content types and exact match mode
- Added CSV export on DHIS2 data elements, indicators and organisation units

### Updated

- Improved search engine and indexing
- Added last pipeline runs in Dashboard
- Fine-tuned Pipelines UX (more focus on the pipeline themselves)
- Increase session cookie lifetime to 1 year
- Metrics: save query strings for GET requests and add "do not track" decorator" 

### Fixed

- Exclude `.s3keep` files from search

Version 0.14
------------

December 7, 2021

### Added

- CodeMirror editor for DAG configurations
- Ability to re-run a DAG with the same parameters
- Add DAG documentation in run screen
  
### Changed

- Replaced full sync by single object refresh when uploading files to S3

### Fixed

- Fixed sync worker

Version 0.13
------------

- DHIS2 Org units support
- Configurable DAGs
- Terms & conditions
- Metrics
- Read-only buckets
- Added visualizations section with external dashboards
- New tabbed detail page for S3

Version 0.12
------------

- Update pipeline UI
- Update logging info, sync & admin
- Fix for user s3 policy generation

Version 0.11
------------

- Airflow sync
- Postgres connector fine-tuning

Version 0.10
------------

- Support for DHIS2 datasets
- Support for datasource sync queues
- Added simple, toggleable feature flags
- Added the possibility to upload files on S3 from the catalog
- A lot of small improvements (linting, tests...)
