Changelog
=========

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
