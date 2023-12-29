# Changelog

## [0.63.2](https://github.com/BLSQ/openhexa-app/compare/0.63.1...0.63.2) (2023-12-29)


### Bug Fixes

* logout handling for Django 5 ([#619](https://github.com/BLSQ/openhexa-app/issues/619)) ([68a1ff6](https://github.com/BLSQ/openhexa-app/commit/68a1ff62525d2efef86503817cb81bace283d3bc))


### Miscellaneous

* remove TOS ([#618](https://github.com/BLSQ/openhexa-app/issues/618)) ([e669fb7](https://github.com/BLSQ/openhexa-app/commit/e669fb70659faa828d9b3dbea60afe4d8677f3c0))

## [0.63.1](https://github.com/BLSQ/openhexa-app/compare/0.63.0...0.63.1) (2023-12-29)


### Bug Fixes

* **Pipelines:** Fix boolean -&gt; bool for the pipeline webhook ([#616](https://github.com/BLSQ/openhexa-app/issues/616)) ([61c37e8](https://github.com/BLSQ/openhexa-app/commit/61c37e895df1ed32d92cd16669fa98a890765352))


### Miscellaneous

* Django 5 and deps overhaul ([#615](https://github.com/BLSQ/openhexa-app/issues/615)) ([491c540](https://github.com/BLSQ/openhexa-app/commit/491c5405033e337b5eccdfd21fdae4ed802f262d))
* Keep comm with JupyterHub API internal to the Docker network ([#599](https://github.com/BLSQ/openhexa-app/issues/599)) ([fed8574](https://github.com/BLSQ/openhexa-app/commit/fed8574eb34321f184d4dc2dfda7ec317a7a55e9))

## [0.63.0](https://github.com/BLSQ/openhexa-app/compare/0.62.0...0.63.0) (2023-12-26)


### Features

* **Pipelines:** Improve webhook support ([#611](https://github.com/BLSQ/openhexa-app/issues/611)) ([b3564c2](https://github.com/BLSQ/openhexa-app/commit/b3564c2a2905d5bd800adba49c30e71da98ebb3e))


### Bug Fixes

* remove django-tailwind commands and adapt documentation ([#612](https://github.com/BLSQ/openhexa-app/issues/612)) ([39cd9cc](https://github.com/BLSQ/openhexa-app/commit/39cd9cc60c80ea91d7ccb6b4bd2b86cc6b1476d1))


### Miscellaneous

* remove catalog sync buttons ([#610](https://github.com/BLSQ/openhexa-app/issues/610)) ([63a0ccd](https://github.com/BLSQ/openhexa-app/commit/63a0ccdd999e391e1f7e17d5001ef7fc507c8d5a))
* remove unused variable declaration ([3017d70](https://github.com/BLSQ/openhexa-app/commit/3017d701875e041de346ceed2b88e6622a2dbe17))

## [0.62.0](https://github.com/BLSQ/openhexa-app/compare/0.61.3...0.62.0) (2023-12-19)


### Features

* better logging for pipelines ([#607](https://github.com/BLSQ/openhexa-app/issues/607)) ([4b98880](https://github.com/BLSQ/openhexa-app/commit/4b9888008d96ba23515df573963cb7295b824bda))
* **Pipelines:** Implement a REST endpoint to run pipelines ([#608](https://github.com/BLSQ/openhexa-app/issues/608)) ([dd6c0db](https://github.com/BLSQ/openhexa-app/commit/dd6c0db79383a78e3fb6e3653910901d10cffbd6))


### Miscellaneous

* disable quick search ([eaa43f6](https://github.com/BLSQ/openhexa-app/commit/eaa43f63b66bea4469918271e16a59eca49b6a40))

## [0.61.3](https://github.com/BLSQ/openhexa-app/compare/0.61.2...0.61.3) (2023-12-12)


### Bug Fixes

* **Workspace:** fix multiple invitations to workspaces for a single user ([#604](https://github.com/BLSQ/openhexa-app/issues/604)) ([8a1dfaa](https://github.com/BLSQ/openhexa-app/commit/8a1dfaa153a9690b483dc8b208a4773c39f25a98))


### Miscellaneous

* **Catalog:** keep only basic details for each datasource ([#603](https://github.com/BLSQ/openhexa-app/issues/603)) ([1d63bf3](https://github.com/BLSQ/openhexa-app/commit/1d63bf3e1604c4e63db21c20a6e951512fae8d30))

## [0.61.2](https://github.com/BLSQ/openhexa-app/compare/0.61.1...0.61.2) (2023-12-06)


### Bug Fixes

* **Pipelines:** check if user can delete pipeline ([#601](https://github.com/BLSQ/openhexa-app/issues/601)) ([963328f](https://github.com/BLSQ/openhexa-app/commit/963328f5de35fa4ae4bf2ae1fdbd6f674fa9f278))

## [0.61.1](https://github.com/BLSQ/openhexa-app/compare/0.61.0...0.61.1) (2023-12-04)


### Bug Fixes

* **Pipelines:** run pipeline with cloudrun argument ([#600](https://github.com/BLSQ/openhexa-app/issues/600)) ([bcc9b4e](https://github.com/BLSQ/openhexa-app/commit/bcc9b4e93bc4e1e8835d1946ee550adb7bde9e69))
* **Workspaces:** add created_by when creating workspace ([#596](https://github.com/BLSQ/openhexa-app/issues/596)) ([a91682f](https://github.com/BLSQ/openhexa-app/commit/a91682f805c3c46a24b6f5459ceae1bbabbab015))

## [0.61.0](https://github.com/BLSQ/openhexa-app/compare/0.60.13...0.61.0) (2023-11-24)


### Features

* **Workspaces:** allow user to specify workspace docker image ([#590](https://github.com/BLSQ/openhexa-app/issues/590)) ([4f69cd5](https://github.com/BLSQ/openhexa-app/commit/4f69cd5072110d403848801f5eb804f7218ac4c9))


### Miscellaneous

* **Connections:** hide s3 secret access key ([#593](https://github.com/BLSQ/openhexa-app/issues/593)) ([cb7c350](https://github.com/BLSQ/openhexa-app/commit/cb7c3505d2efa30019d4163f45f507e4c152df32))
* merge migration ([949f657](https://github.com/BLSQ/openhexa-app/commit/949f6571cb6cfaa9c714178dd03b24237217e9d2))
* release please bump policy change ([#597](https://github.com/BLSQ/openhexa-app/issues/597)) ([3bfb241](https://github.com/BLSQ/openhexa-app/commit/3bfb241a50b7bf8ecd834f4224896c57c63734df))
* **Visualizations:** remove app folder ([#594](https://github.com/BLSQ/openhexa-app/issues/594)) ([ca0261e](https://github.com/BLSQ/openhexa-app/commit/ca0261e8df66ec2ecfe417df91607035702a0d5f))

## [0.60.13](https://github.com/BLSQ/openhexa-app/compare/0.60.12...0.60.13) (2023-11-20)


### Bug Fixes

* Fix permission check for dataset download ([#591](https://github.com/BLSQ/openhexa-app/issues/591)) ([a6a2c59](https://github.com/BLSQ/openhexa-app/commit/a6a2c596275b5cf15934318abcb2954e73f171cc))

## [0.60.12](https://github.com/BLSQ/openhexa-app/compare/0.60.11...0.60.12) (2023-11-13)


### Bug Fixes

* **Core:** collecstatic files ([#587](https://github.com/BLSQ/openhexa-app/issues/587)) ([fbf25e9](https://github.com/BLSQ/openhexa-app/commit/fbf25e955635cb5fe1aca96285dddb801b4619d1))

## [0.60.11](https://github.com/BLSQ/openhexa-app/compare/0.60.10...0.60.11) (2023-11-10)


### Bug Fixes

* Add default value for AWS_DEFAULT_REGION in env dist file so that tests can pass on a fresh local install ([#578](https://github.com/BLSQ/openhexa-app/issues/578)) ([11c8929](https://github.com/BLSQ/openhexa-app/commit/11c89299a32710f7942bd7d2f296489734027c14))
* **Core:** Replace deprecated CIEmailField with EmailField ([#580](https://github.com/BLSQ/openhexa-app/issues/580)) ([e9d81ba](https://github.com/BLSQ/openhexa-app/commit/e9d81ba6120c692e83a1724aac00bc84a5a42e45))
* Update autoflake and flake8 ([0c58dac](https://github.com/BLSQ/openhexa-app/commit/0c58dac4deb1f58f3db3a7bb16e5e26223357c72))
* Use blsq/openhexa-base-notebook:latest by default for pipelines ([#581](https://github.com/BLSQ/openhexa-app/issues/581)) ([e62681f](https://github.com/BLSQ/openhexa-app/commit/e62681fcb2b67c87b69c6a0c77cffa74ef5d44ea))


### Miscellaneous

* remove visualizations app (step 1) ([#585](https://github.com/BLSQ/openhexa-app/issues/585)) ([a20933c](https://github.com/BLSQ/openhexa-app/commit/a20933cdcf4c4f52db90878eb62e1fd95b8f27c7))

## [0.60.10](https://github.com/BLSQ/openhexa-app/compare/0.60.9...0.60.10) (2023-10-18)


### Bug Fixes

* **Files:** order bucket prefixes ([#575](https://github.com/BLSQ/openhexa-app/issues/575)) ([1e095fe](https://github.com/BLSQ/openhexa-app/commit/1e095fe2ece8064bdd82490acc8bf2e756ac7579))
* **Pipelines:** add timeout to PipelineRun model ([#570](https://github.com/BLSQ/openhexa-app/issues/570)) ([f4c1bbf](https://github.com/BLSQ/openhexa-app/commit/f4c1bbfe8458595bfd03b7a83fed58d3dc8723ff))
* **Pipelines:** allow scheduling of pipelines if they have optional / default parameters ([#572](https://github.com/BLSQ/openhexa-app/issues/572)) ([80d1ce6](https://github.com/BLSQ/openhexa-app/commit/80d1ce63b9ccf59e468734eff0366a8773ff7f8f))


### Miscellaneous

* Upgrade most dependencies ([#576](https://github.com/BLSQ/openhexa-app/issues/576)) ([cbadcfa](https://github.com/BLSQ/openhexa-app/commit/cbadcfaffba7f0edc26e457d41f397836fe3806f))
* **Workspaces:** add tests for connections env variables ([#573](https://github.com/BLSQ/openhexa-app/issues/573)) ([e68c007](https://github.com/BLSQ/openhexa-app/commit/e68c007683d0784eb57293fbbfba29d1ba5ac5ec))

## [0.60.9](https://github.com/BLSQ/openhexa-app/compare/0.60.8...0.60.9) (2023-10-11)


### Bug Fixes

* **Connections:** add _API_URL env variable for Iaso connections (backwards-compatibility) ([#568](https://github.com/BLSQ/openhexa-app/issues/568)) ([a92ffc4](https://github.com/BLSQ/openhexa-app/commit/a92ffc4d49681126b6c068fb096c3474e987704e))

## [0.60.8](https://github.com/BLSQ/openhexa-app/compare/0.60.7...0.60.8) (2023-10-09)


### Bug Fixes

* **Connections:** rename IASO connection api_url to url ([#566](https://github.com/BLSQ/openhexa-app/issues/566)) ([c68ab2d](https://github.com/BLSQ/openhexa-app/commit/c68ab2df70cf81796cb2df41abc02b7fabe5972e))

## [0.60.7](https://github.com/BLSQ/openhexa-app/compare/0.60.6...0.60.7) (2023-10-02)


### Bug Fixes

* Do not allow slugs for workspace, datasets & connection to have double dash ([#562](https://github.com/BLSQ/openhexa-app/issues/562)) ([1199cfb](https://github.com/BLSQ/openhexa-app/commit/1199cfbfa6ed0894c488ab43b82b3a9242e1e975))
* **Workspaces:** don't test for access tokens in resolve_generate_workspace_token ([#560](https://github.com/BLSQ/openhexa-app/issues/560)) ([c54b1a9](https://github.com/BLSQ/openhexa-app/commit/c54b1a93d9781c1e58a5b84392ce4669b3a24e0c))

## [0.60.6](https://github.com/BLSQ/openhexa-app/compare/0.60.5...0.60.6) (2023-09-27)


### Bug Fixes

* **Databases:** get_table_rows has to take the page_size from the db return ([#558](https://github.com/BLSQ/openhexa-app/issues/558)) ([4c212d8](https://github.com/BLSQ/openhexa-app/commit/4c212d8196b002dc8feb3183b5ca47a4ef381d5b))

## [0.60.5](https://github.com/BLSQ/openhexa-app/compare/0.60.4...0.60.5) (2023-09-27)


### Bug Fixes

* **datasets:** Make the datasets working with pipelines ([#556](https://github.com/BLSQ/openhexa-app/issues/556)) ([27358eb](https://github.com/BLSQ/openhexa-app/commit/27358ebc15247ff98310777fe3d565a12cbcb368))

## [0.60.4](https://github.com/BLSQ/openhexa-app/compare/0.60.3...0.60.4) (2023-09-25)


### Bug Fixes

* **Workspaces:** set access_token directly in migration ([#554](https://github.com/BLSQ/openhexa-app/issues/554)) ([954ea94](https://github.com/BLSQ/openhexa-app/commit/954ea94f1ded0972e3179c088a93629fae035ef9))

## [0.60.3](https://github.com/BLSQ/openhexa-app/compare/0.60.2...0.60.3) (2023-09-25)


### Features

* **Pipelines:** add timeout to PipelineRun model ([#549](https://github.com/BLSQ/openhexa-app/issues/549)) ([294fc44](https://github.com/BLSQ/openhexa-app/commit/294fc44812c788144fd306e6df5765e395891b7a))


### Bug Fixes

* **Workspaces:** ensure the presence of a token / server hash in memberships ([#552](https://github.com/BLSQ/openhexa-app/issues/552)) ([1f1c4da](https://github.com/BLSQ/openhexa-app/commit/1f1c4da6f3413a3810b61339cf5be233f587a915))

## [0.60.2](https://github.com/BLSQ/openhexa-app/compare/0.60.1...0.60.2) (2023-09-19)


### Features

* **Datasets:** add fileByName on dataset's version, datasets ([#548](https://github.com/BLSQ/openhexa-app/issues/548)) ([ba1c23a](https://github.com/BLSQ/openhexa-app/commit/ba1c23a08a7aabd02a9a027dc7d9ae538b58e4dd))
* **Pipelines:** allow scheduling if all params have default value ([#542](https://github.com/BLSQ/openhexa-app/issues/542)) ([5e6f4b8](https://github.com/BLSQ/openhexa-app/commit/5e6f4b8639e7cb601ac1c7c9048a346b7bfad9f5))

## [0.60.1](https://github.com/BLSQ/openhexa-app/compare/0.60.0...0.60.1) (2023-09-14)


### Features

* **Connections:** migration to hide service account key value ([#544](https://github.com/BLSQ/openhexa-app/issues/544)) ([b546c7c](https://github.com/BLSQ/openhexa-app/commit/b546c7ccb7afcd2c78e922cf4d7abbd55cd541b6))


### Bug Fixes

* **datasets:** Fix get_file_by_name for a version ([#546](https://github.com/BLSQ/openhexa-app/issues/546)) ([10bb6e4](https://github.com/BLSQ/openhexa-app/commit/10bb6e474b8ff2fac215776fdd4c45bbc05f9508))

## [0.60.0](https://github.com/BLSQ/openhexa-app/compare/0.59.0...0.60.0) (2023-09-12)


### Features

* **Datasets:** Implement workspace datasets & sharing ([#533](https://github.com/BLSQ/openhexa-app/issues/533)) ([fcd8f19](https://github.com/BLSQ/openhexa-app/commit/fcd8f1903ead55d0869175a98ec1581c1d91c381))


### Miscellaneous

* **releases:** Prepare next release 0.60.0 ([50f4bb1](https://github.com/BLSQ/openhexa-app/commit/50f4bb1c71ffa5451b3de74fb41fd1d22351a824))

## [0.59.0](https://github.com/BLSQ/openhexa-app/compare/0.58.13...0.59.0) (2023-09-12)


### Bug Fixes

* **Connections:** abort connection creation transaction if an error occurs ([#541](https://github.com/BLSQ/openhexa-app/issues/541)) ([c0fbd85](https://github.com/BLSQ/openhexa-app/commit/c0fbd85a5b025e9f6fdbaa65913dd899a9f5eb86))
* **Pipelines:** generate random string to avoid pod names collision ([#539](https://github.com/BLSQ/openhexa-app/issues/539)) ([0bcf78f](https://github.com/BLSQ/openhexa-app/commit/0bcf78f33b84fe1c71b176d0c8984586115fc88c))


### Miscellaneous

* **Releases:** Prepare release 0.59.0 ([baa67b5](https://github.com/BLSQ/openhexa-app/commit/baa67b5c5dac3dfec46de56c51aa30918b588484))

## [0.58.13](https://github.com/BLSQ/openhexa-app/compare/0.58.12...0.58.13) (2023-08-22)


### Features

* admin improvements ([#532](https://github.com/BLSQ/openhexa-app/issues/532)) ([1aa130d](https://github.com/BLSQ/openhexa-app/commit/1aa130de60d0e92199d9c0fa3f46d9e5c4b42a86))


### Bug Fixes

* **Workspaces:** Add the 'workspaces' feature to legacy users invited in a workspace ([#537](https://github.com/BLSQ/openhexa-app/issues/537)) ([ed6fedf](https://github.com/BLSQ/openhexa-app/commit/ed6fedff7a1c4709ec003bb96ed9115cec1101ad))
* **Workspaces:** filter invitations by user and workspace ([#538](https://github.com/BLSQ/openhexa-app/issues/538)) ([bf99e12](https://github.com/BLSQ/openhexa-app/commit/bf99e128f424c3d3ae9555418b5b219254aefcc8))


### Miscellaneous

* remove IASO connector (step 2) ([#531](https://github.com/BLSQ/openhexa-app/issues/531)) ([90a8410](https://github.com/BLSQ/openhexa-app/commit/90a8410995a48c1c495ba09533a8724b1272cb29))

## [0.58.12](https://github.com/BLSQ/openhexa-app/compare/0.58.11...0.58.12) (2023-08-18)


### Bug Fixes

* **Pipelines:** Do not throw an error when an output does not exist anymore ([#534](https://github.com/BLSQ/openhexa-app/issues/534)) ([ba75bdb](https://github.com/BLSQ/openhexa-app/commit/ba75bdb5d3ce29348df6ccce85920ec09515debd))

## [0.58.11](https://github.com/BLSQ/openhexa-app/compare/0.58.10...0.58.11) (2023-08-14)


### Bug Fixes

* **Pipelines:** set timeout field on PipelineVersion model ([#529](https://github.com/BLSQ/openhexa-app/issues/529)) ([5f33e27](https://github.com/BLSQ/openhexa-app/commit/5f33e27c3c906329ff5738f17d9ba01a6b4389f6))

## [0.58.10](https://github.com/BLSQ/openhexa-app/compare/0.58.9...0.58.10) (2023-08-14)


### Miscellaneous

* remove print ([0ea5890](https://github.com/BLSQ/openhexa-app/commit/0ea5890305e2db01ded9b4d18281cfa5796c0eee))

## [0.58.9](https://github.com/BLSQ/openhexa-app/compare/0.58.8...0.58.9) (2023-08-14)


### Features

* **Pipelines:** Try to convert raw outputs to database table or bucket ([#518](https://github.com/BLSQ/openhexa-app/issues/518)) ([9f7bc27](https://github.com/BLSQ/openhexa-app/commit/9f7bc274423512e1d3b55a8d5b9a67bce3e1dbb2))
* **Workspaces:** improve invitation management ([#523](https://github.com/BLSQ/openhexa-app/issues/523)) ([10dcb8f](https://github.com/BLSQ/openhexa-app/commit/10dcb8fc0d1203a343f2871962adb41927c8639e))


### Bug Fixes

* **files:** Break when we have enough objects (and before loading the next page) ([#525](https://github.com/BLSQ/openhexa-app/issues/525)) ([204be98](https://github.com/BLSQ/openhexa-app/commit/204be98dc7bb8f103a4a0d9911f51a9c8f25872c))

## [0.58.8](https://github.com/BLSQ/openhexa-app/compare/0.58.7...0.58.8) (2023-08-09)


### Bug Fixes

* Revert not ready commit ([090e638](https://github.com/BLSQ/openhexa-app/commit/090e6386fbfc50c055e9b5966c6e6a5ecf66ecdb))

## [0.58.7](https://github.com/BLSQ/openhexa-app/compare/0.58.6...0.58.7) (2023-08-09)


### Bug Fixes

* **Pipelines:** Add missing command to pod creation ([6e68334](https://github.com/BLSQ/openhexa-app/commit/6e68334ae3c3e9136bef7e8dd41ad6c5b9ea5dc9))

## [0.58.6](https://github.com/BLSQ/openhexa-app/compare/0.58.5...0.58.6) (2023-08-08)


### Miscellaneous

* fix release ([311d504](https://github.com/BLSQ/openhexa-app/commit/311d504872e03d745e6ad38ce8404b5cb841bc68))
* fix release ([6b9e25f](https://github.com/BLSQ/openhexa-app/commit/6b9e25f25222f015562fd9260d370c6ddd2b3d40))
* **main:** release 0.58.5 ([#520](https://github.com/BLSQ/openhexa-app/issues/520)) ([0040f36](https://github.com/BLSQ/openhexa-app/commit/0040f3629ec32459da99e269463a5adce813cb6f))

## [0.58.5](https://github.com/BLSQ/openhexa-app/compare/0.58.5...0.58.5) (2023-08-08)


### Miscellaneous

* fix release ([6b9e25f](https://github.com/BLSQ/openhexa-app/commit/6b9e25f25222f015562fd9260d370c6ddd2b3d40))

## [0.58.5](https://github.com/BLSQ/openhexa-app/compare/0.58.4...0.58.5) (2023-08-08)


### Bug Fixes

* **pipelines:** Use the new command 'cloudrun' in k8s & pass config as expected ([e660199](https://github.com/BLSQ/openhexa-app/commit/e660199beb2bf688e61404fbd38d3e4ed11c5b51))

## [0.58.4](https://github.com/BLSQ/openhexa-app/compare/0.58.3...0.58.4) (2023-08-08)


### Features

* **Files:** Show/hide hidden files & directories ([#517](https://github.com/BLSQ/openhexa-app/issues/517)) ([8033cce](https://github.com/BLSQ/openhexa-app/commit/8033cce28e63dff7549391678cf4742f5ad965ce))
* **Pipelines:** define timeout for pipeline run ([#515](https://github.com/BLSQ/openhexa-app/issues/515)) ([ce4fc62](https://github.com/BLSQ/openhexa-app/commit/ce4fc6240f97ade1db4d671e0f3a9a0e50f8218c))

## [0.58.3](https://github.com/BLSQ/openhexa-app/compare/0.58.2...0.58.3) (2023-07-31)


### Miscellaneous

* **deps-dev:** bump socket.io-parser in /hexa/ui/static_src ([#503](https://github.com/BLSQ/openhexa-app/issues/503)) ([68614c2](https://github.com/BLSQ/openhexa-app/commit/68614c27b0e5319459ec0aba94f556035f9630d5))
* **deps:** bump yaml from 2.2.1 to 2.2.2 in /hexa/ui/static_src ([#464](https://github.com/BLSQ/openhexa-app/issues/464)) ([9263dd2](https://github.com/BLSQ/openhexa-app/commit/9263dd21b6a173659ffb26af6362a60a18831344))

## [0.58.2](https://github.com/BLSQ/openhexa-app/compare/0.58.1...0.58.2) (2023-07-24)


### Features

* **Workspaces:** set demo data optional ([#511](https://github.com/BLSQ/openhexa-app/issues/511)) ([10d79d4](https://github.com/BLSQ/openhexa-app/commit/10d79d4644e29f114a0494e7648349e1d6b0be94))

## [0.58.1](https://github.com/BLSQ/openhexa-app/compare/0.58.0...0.58.1) (2023-07-20)


### Features

* **Pipelines:** prevent push of version with params for scheduled pipeline. ([#507](https://github.com/BLSQ/openhexa-app/issues/507)) ([8d58d3c](https://github.com/BLSQ/openhexa-app/commit/8d58d3c00e8ce03fb3b63f5d32f7edb0d460e9c1))
* **Workspaces:** add workspace invitations list to django admin ([#508](https://github.com/BLSQ/openhexa-app/issues/508)) ([b4ac2ba](https://github.com/BLSQ/openhexa-app/commit/b4ac2baa1d5ec3363b11584df6b55cec3e35d650))
* **Workspaces:** Automatically log in users after signup ([#510](https://github.com/BLSQ/openhexa-app/issues/510)) ([a06e9ad](https://github.com/BLSQ/openhexa-app/commit/a06e9adaaccff105019d15782e109ad0d9edc499))


### Bug Fixes

* **ConnectionFields:** order fields by creation date ([#506](https://github.com/BLSQ/openhexa-app/issues/506)) ([0c8c494](https://github.com/BLSQ/openhexa-app/commit/0c8c4948cf9fd5ad00dc80b2fdb60206b7818ffe))

## [0.58.0](https://github.com/BLSQ/openhexa-app/compare/0.57.6...0.58.0) (2023-07-19)


### Bug Fixes

* **Connections:** Add a suffix to connection slug if it exists ([#505](https://github.com/BLSQ/openhexa-app/issues/505)) ([d32d2fb](https://github.com/BLSQ/openhexa-app/commit/d32d2fb61f9d1043bd5833af2439036de80d2480))


### Miscellaneous

* Configure release-please ([#502](https://github.com/BLSQ/openhexa-app/issues/502)) ([b970ee4](https://github.com/BLSQ/openhexa-app/commit/b970ee46fc3648a39ac9919a3fee18e80e2e25d0))
* **Connections:** Limit slug to 40 chars ([9c0e188](https://github.com/BLSQ/openhexa-app/commit/9c0e188156a71a5916103c72f51f1dba743e2259))
* **Pipelines:** add schedule permission ([#501](https://github.com/BLSQ/openhexa-app/issues/501)) ([a5afa79](https://github.com/BLSQ/openhexa-app/commit/a5afa79251cb904813396d80eac39b97b92bdd40))
* **Release:** Release 0.58.0 ([1997a4b](https://github.com/BLSQ/openhexa-app/commit/1997a4be92167aafa09b6c81cdeff278d6abfe32))
* Remove data_collections STEP 2 ([#496](https://github.com/BLSQ/openhexa-app/issues/496)) ([52c537d](https://github.com/BLSQ/openhexa-app/commit/52c537de3fabc1500778c5b6ce8cea2865dde17c))

Changelog
=========

Version 0.46
------------

August 17, 2022

### Added

- Collections mutations

### Fixed



Version 0.45
------------

August 8, 2022

### Added

- Collections data model
- Inject IASO use API token into notebooks
- Add feature flag for git in notebooks + pass it to notebooks componen

### Fixed

- Fix column's widths of the data grid

Version 0.44
------------

August 2, 2022

### Added

- First version of Iaso connector plugin

Version 0.43
------------

July 26, 2022

### Updated

- Refactored S3 credentials and align notebooks / pipelines

### Fixed

- Fixed AccessMod Zonal Stats travel times validation

Version 0.42
------------

July 19, 2022

### Added

- Support for public S3 buckets

### Fixed

- Pinned rasterio / rio-cogeo to avoid compression issues in latest versions

Version 0.41
------------

July 11, 2022

### Added

- Added upload/download feature for GCS objects in the catalog

### Updated

- Most Python dependencies have been updated

### Fixed

- Fixed double-slash issue for S3 directories links in the catalog

Version 0.40
------------

June 21, 2022

### Added

- Country module support sub zone by countries

### Updated

- After validating a AccessMod fileset, update related analysis status

Version 0.39
------------

May 31, 2022

### Added

- Support for Google Cloud Storage for notebooks
- Country module for storing list of countries, boundaries, flags...
- AccessMod: new analysis: zonal statistics

### Updated

- Allow update of AccessMod filesets
- Accessibility analysis improved configuration, parameters
- Generate only one image for openhexa-app and AccessMod data worker
- DHIS2 Sync is not atomic anymore, it was causing a lot of SQL load

Version 0.38
------------

May 24, 2022

Mostly AccessMod-related development prior to production release.

Version 0.37
------------

May 17, 2022

Mostly AccessMod-related development prior to production release.

Version 0.36
------------

May 12, 2022

### Added

- AccessMod: input validation

### Updated

- AccessMod: configuration format for new analysis version

Version 0.35
------------

May 3, 2022

### Added

- New, more flexible permission system
- Validation / processing background worker
- Support for public buckets

### Updated

- Fine-tuned AccessMod graph

Version 0.34
------------

April 26, 2022

### Added

- New image build process for data processing and validation

### Fixed

- Fixed MultiplePermission error in DHIS2 datacard

Version 0.33
------------

April 19, 2022

Maintenance / AccessMod release

Version 0.32
------------

April 12, 2022

Maintenance / AccessMod release

Version 0.31
------------

April 5, 2022

### Added

- Reset password API
- Teams & permissions API first steps

### Updated

- Updated all Python dependencies
- Fine-tune linting

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
