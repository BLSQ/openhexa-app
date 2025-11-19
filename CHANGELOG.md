# Changelog

## [2.12.0](https://github.com/BLSQ/openhexa-app/compare/2.11.0...2.12.0) (2025-11-19)


### Features

* add publisher property to template pipelines  ([#1439](https://github.com/BLSQ/openhexa-app/issues/1439)) ([abcdb0c](https://github.com/BLSQ/openhexa-app/commit/abcdb0c26bb5b6448d4bbfa40f4ba03ca30fce95))

## [2.11.0](https://github.com/BLSQ/openhexa-app/compare/2.10.0...2.11.0) (2025-11-19)


### Features

* Add application_name parameter to Postgres connections from Pipelines (HEXA-1419) ([#1460](https://github.com/BLSQ/openhexa-app/issues/1460)) ([d91b83b](https://github.com/BLSQ/openhexa-app/commit/d91b83b5c34390141fae976b9cf95e60643b97df))
* expose public key used to deliver jwt token ([#1464](https://github.com/BLSQ/openhexa-app/issues/1464)) ([2f06e50](https://github.com/BLSQ/openhexa-app/commit/2f06e5077b5e9aaa8a2c4438c7ca3a9592540d79))
* implements shortcuts app and extend webapps with shortcuts ([#1453](https://github.com/BLSQ/openhexa-app/issues/1453)) ([e7c7b7b](https://github.com/BLSQ/openhexa-app/commit/e7c7b7b07a76bc38d3b4a56fb644fe6131751de6))
* refactor the pipelines runner process to be stateless (HEXA-1417) ([#1463](https://github.com/BLSQ/openhexa-app/issues/1463)) ([6eaea5e](https://github.com/BLSQ/openhexa-app/commit/6eaea5e64c2a70195b12cba5977215e021cad43c))


### Bug Fixes

* add CNAME file to docs directory for GitHub Pages deployment ([fce4bfc](https://github.com/BLSQ/openhexa-app/commit/fce4bfce4b0c446085b12d3d21eddae3a837c0e0))
* configure mkdocs to properly serve documentation site ([#1478](https://github.com/BLSQ/openhexa-app/issues/1478)) ([748e2e9](https://github.com/BLSQ/openhexa-app/commit/748e2e973178483350444175534b8ef68edc2480))
* jupyter lab pod not starting due to lack of workspace membership (HEXA-1392) ([#1458](https://github.com/BLSQ/openhexa-app/issues/1458)) ([2c5867a](https://github.com/BLSQ/openhexa-app/commit/2c5867a06a07efb91813f1e2c94a977b5a651548))
* remove empty elemnts from documentation ([f5ef6ff](https://github.com/BLSQ/openhexa-app/commit/f5ef6ffe322bdb0e7a619574dba92e399fd8fd4d))
* remove Spanish and Portuguese translations, keep only English and French ([f48e812](https://github.com/BLSQ/openhexa-app/commit/f48e8126c469730f393f169a0c6640c60b424573))

## [2.10.0](https://github.com/BLSQ/openhexa-app/compare/2.9.1...2.10.0) (2025-11-03)


### Features

* as an organization owner or admin i want to manage the organization settings (PATHWAYS-967) ([#1456](https://github.com/BLSQ/openhexa-app/issues/1456)) ([28be58a](https://github.com/BLSQ/openhexa-app/commit/28be58a7c519b7bef4bcc41a7b1e85ffb5aac491))

## [2.9.1](https://github.com/BLSQ/openhexa-app/compare/2.9.0...2.9.1) (2025-10-30)


### Bug Fixes

* templates should be taken globally ([#1454](https://github.com/BLSQ/openhexa-app/issues/1454)) ([743985b](https://github.com/BLSQ/openhexa-app/commit/743985ba709e3c0b335dbf65032465a1a50b86c5))

## [2.9.0](https://github.com/BLSQ/openhexa-app/compare/2.8.0...2.9.0) (2025-10-30)


### Features

* add workspace scoping for pipeline tag search similar as in pipeline tempaltes ([#1451](https://github.com/BLSQ/openhexa-app/issues/1451)) ([db6a1fa](https://github.com/BLSQ/openhexa-app/commit/db6a1fae1cadc6a2f2be0116dc5c9f65aa893272))


### Bug Fixes

* add distinct to fix tags join ([#1448](https://github.com/BLSQ/openhexa-app/issues/1448)) ([1556684](https://github.com/BLSQ/openhexa-app/commit/1556684e8f2025c18d837d35f073fd2fb2ae19a2))
* redirects from organization pages after removing the feature flag  ([#1450](https://github.com/BLSQ/openhexa-app/issues/1450)) ([8e78ebc](https://github.com/BLSQ/openhexa-app/commit/8e78ebc5cad448d07cb955f706cff635ab857970))

## [2.8.0](https://github.com/BLSQ/openhexa-app/compare/2.7.1...2.8.0) (2025-10-29)


### Features

* add issueWorkspaceToken endpoint to generate a JWT token ([#1446](https://github.com/BLSQ/openhexa-app/issues/1446)) ([41c5292](https://github.com/BLSQ/openhexa-app/commit/41c5292d145a721ec96979af114c3a2ed3446a20))
* enable pipeline template sorting with a generic approach ([#1433](https://github.com/BLSQ/openhexa-app/issues/1433)) ([6e7862f](https://github.com/BLSQ/openhexa-app/commit/6e7862f8f91fc70e208088cd91f5b41ef094ac52))


### Bug Fixes

* pipeline runner zombie reaper should kill runners with meaningful message and status (HEXA-1413) ([#1445](https://github.com/BLSQ/openhexa-app/issues/1445)) ([e908ff5](https://github.com/BLSQ/openhexa-app/commit/e908ff50093f55f1143f2141ab4f14a48ae9dc6e))

## [2.7.1](https://github.com/BLSQ/openhexa-app/compare/2.7.0...2.7.1) (2025-10-28)


### Bug Fixes

* allow superusers to see pipelines in a workspace they are not member of (HEXA-1407) ([#1442](https://github.com/BLSQ/openhexa-app/issues/1442)) ([9432e0c](https://github.com/BLSQ/openhexa-app/commit/9432e0c44aeca8d2868d64102353ea2258b7e94b))

## [2.7.0](https://github.com/BLSQ/openhexa-app/compare/2.6.2...2.7.0) (2025-10-27)


### Features

* add download code to templates ([#1412](https://github.com/BLSQ/openhexa-app/issues/1412)) ([115a07e](https://github.com/BLSQ/openhexa-app/commit/115a07e98c9811aadd27c74e5c8c61fd76f218f7))
* extend tags and functional types to template pipelines ([#1405](https://github.com/BLSQ/openhexa-app/issues/1405)) ([150cf64](https://github.com/BLSQ/openhexa-app/commit/150cf641bce01aa1d772f4fdbcb87a76dcf78d35))
* remove feature flag of Organization ([#1429](https://github.com/BLSQ/openhexa-app/issues/1429)) ([021f4bb](https://github.com/BLSQ/openhexa-app/commit/021f4bbf3a5c0ee7e19ac9d44a157c6e15aebdcb))


### Bug Fixes

* add a loader to direct workspace invitation query + optimize a little bit the query ([#1431](https://github.com/BLSQ/openhexa-app/issues/1431)) ([b61e8b0](https://github.com/BLSQ/openhexa-app/commit/b61e8b085fd960d076379551295d1375af9ea70a))
* apollo version (HEXA-1370)([#1440](https://github.com/BLSQ/openhexa-app/issues/1440)) ([8fe7b37](https://github.com/BLSQ/openhexa-app/commit/8fe7b37d5ab31c931440363c9843cf89a3369270))
* pipeline heartbeat resolver (HEXA-1406) ([#1441](https://github.com/BLSQ/openhexa-app/issues/1441)) ([fba6aef](https://github.com/BLSQ/openhexa-app/commit/fba6aef9d7000cc706d35c28877e2a0e1f688627))
* pipelines should have access to organization shared dataset (PATHWAYS-869) ([#1435](https://github.com/BLSQ/openhexa-app/issues/1435)) ([8950017](https://github.com/BLSQ/openhexa-app/commit/8950017d273074b0d5278a060fa1aae2ff036ed1))
* Renovate pip-compile dependency detection ([#1428](https://github.com/BLSQ/openhexa-app/issues/1428)) ([8d0d1e6](https://github.com/BLSQ/openhexa-app/commit/8d0d1e6235902c67900d124d6ac250ec25d0bf02))
* superusers should be able to access all datasets (HEXA-1396) ([#1427](https://github.com/BLSQ/openhexa-app/issues/1427)) ([5d288f2](https://github.com/BLSQ/openhexa-app/commit/5d288f21725095079f4bb7ac7d60558f11dc3490))

## [2.6.2](https://github.com/BLSQ/openhexa-app/compare/2.6.1...2.6.2) (2025-10-16)


### Bug Fixes

* Update openhexa sdk + toolbox dependencies ([#1424](https://github.com/BLSQ/openhexa-app/issues/1424)) ([39fa255](https://github.com/BLSQ/openhexa-app/commit/39fa255d769a28e359c52a6aaeba0efbe571678a))

## [2.6.1](https://github.com/BLSQ/openhexa-app/compare/2.6.0...2.6.1) (2025-10-15)


### Bug Fixes

* add a warning message when deleting access to org admins/owners (HEXA-1384) ([#1418](https://github.com/BLSQ/openhexa-app/issues/1418)) ([3d815cb](https://github.com/BLSQ/openhexa-app/commit/3d815cbbba07434d4d05f0d510a955c10cb27251))
* truncate dataset name in the org page ([#1423](https://github.com/BLSQ/openhexa-app/issues/1423))(PATHWAYS-982) ([40f0397](https://github.com/BLSQ/openhexa-app/commit/40f0397d4828976fcec38144442fce51937108b6))

## [2.6.0](https://github.com/BLSQ/openhexa-app/compare/2.5.1...2.6.0) (2025-10-14)


### Features

* enhance pipelines page with new columns and filtering options ([#1404](https://github.com/BLSQ/openhexa-app/issues/1404)) ([4c50ede](https://github.com/BLSQ/openhexa-app/commit/4c50ede20c718029f15dfc3efa4fa613ed0d8113))


### Bug Fixes

* buttons for archive and workspace settings should be disabled if no permissions (PATHWAYS-949) ([#1400](https://github.com/BLSQ/openhexa-app/issues/1400)) ([d6993e9](https://github.com/BLSQ/openhexa-app/commit/d6993e94f8472513bbdd9fd90fb7731d90394d31))
* combobox wrongly set to readonly ([#1407](https://github.com/BLSQ/openhexa-app/issues/1407)) ([842b4c5](https://github.com/BLSQ/openhexa-app/commit/842b4c55a284286fdcdac075fc4e45d3bf597d9c))
* dataset page of organization is slow to load (PATHWAYS-945) ([#1406](https://github.com/BLSQ/openhexa-app/issues/1406)) ([2dfa385](https://github.com/BLSQ/openhexa-app/commit/2dfa3851cbf1d689b936df0b78121b9a3e101a63))
* improve logging for the pipeline heartbeat mechanism + share config to run pipelines on kubernetes locally (HEXA-1386) ([#1395](https://github.com/BLSQ/openhexa-app/issues/1395)) ([f9fcdc2](https://github.com/BLSQ/openhexa-app/commit/f9fcdc2c64201896495f9df451966036f51bdaae))
* inconsistent pending invitations information (HEXA-1390) ([#1408](https://github.com/BLSQ/openhexa-app/issues/1408)) ([5aea352](https://github.com/BLSQ/openhexa-app/commit/5aea352c8fdd238279b350ce83737f5052fde434))
* invite gmail clips the resources section for some reason (PATHWAYS-942) ([#1403](https://github.com/BLSQ/openhexa-app/issues/1403)) ([e9417c8](https://github.com/BLSQ/openhexa-app/commit/e9417c84541d7c7b3166eb0c15091867827a029e))
* superuser permission when not org admin/owner (HEXA-1383) ([#1397](https://github.com/BLSQ/openhexa-app/issues/1397)) ([99962b7](https://github.com/BLSQ/openhexa-app/commit/99962b7d51bec3c71481ef21104815d60521d5c6))
* workspace admins should be able to create workspaces (HEXA-1387) ([#1402](https://github.com/BLSQ/openhexa-app/issues/1402)) ([91c06f5](https://github.com/BLSQ/openhexa-app/commit/91c06f5953ed9abdda8ee38f6da797e4825574ee))

## [2.5.1](https://github.com/BLSQ/openhexa-app/compare/2.5.0...2.5.1) (2025-10-02)


### Reverts

* changes in logging ([d805529](https://github.com/BLSQ/openhexa-app/commit/d80552991ee78ab2f707017f52a972dda6105fae))

## [2.5.0](https://github.com/BLSQ/openhexa-app/compare/2.4.0...2.5.0) (2025-10-02)


### Features

* extend sentry logging ([64f984c](https://github.com/BLSQ/openhexa-app/commit/64f984cbb3c6e79552304b4b987807e757a5f74d))
* **pipelines:** add functional type to pipelines  ([#1380](https://github.com/BLSQ/openhexa-app/issues/1380)) ([9f339c1](https://github.com/BLSQ/openhexa-app/commit/9f339c11b3f507e54ca747f3ad334e205a7f3f03))


### Bug Fixes

* inviting workspace should default to none access level (PATHWAYS-941) ([#1387](https://github.com/BLSQ/openhexa-app/issues/1387)) ([5fb23c7](https://github.com/BLSQ/openhexa-app/commit/5fb23c7c715fcbb20968734fddd0cfc24b689f26))
* Object of type UUID is not JSON serializable for mixpanel events on organization emails ([#1393](https://github.com/BLSQ/openhexa-app/issues/1393)) ([30c3369](https://github.com/BLSQ/openhexa-app/commit/30c3369e015899cdbd090c838067e4ec257a0698))
* update dataset version changelog when switching versions ([#1389](https://github.com/BLSQ/openhexa-app/issues/1389)) ([906e4b8](https://github.com/BLSQ/openhexa-app/commit/906e4b82b5d46d74a47efe843dbdbafc279e674b))

## [2.4.0](https://github.com/BLSQ/openhexa-app/compare/2.3.5...2.4.0) (2025-09-26)


### Features

* enable org admins and owners to do any actions a workspace admin or editor can do (PATHWAYS-891) ([#1378](https://github.com/BLSQ/openhexa-app/issues/1378)) ([39b1260](https://github.com/BLSQ/openhexa-app/commit/39b1260bf25c067469f68db8dc47ae3217591b74))
* enable org admins and owners to see all assets a workspace admin or editor can do (PATHWAYS-914) ([#1379](https://github.com/BLSQ/openhexa-app/issues/1379)) ([c417a08](https://github.com/BLSQ/openhexa-app/commit/c417a08658c27565f7a56bb09d39a8979f985cc8))
* feature flag for workspace creation ([#1374](https://github.com/BLSQ/openhexa-app/issues/1374)) ([23a367c](https://github.com/BLSQ/openhexa-app/commit/23a367c7ad43c9f3979c23ae4c3705466edb7284))
* filter member by role (PATHWAYS-882) ([#1384](https://github.com/BLSQ/openhexa-app/issues/1384)) ([7a0fee1](https://github.com/BLSQ/openhexa-app/commit/7a0fee154fe1cead998fe29c038e04e986ef5dca))
* **pipelines:** add tags to pipelines (HEXA-1298) ([#1368](https://github.com/BLSQ/openhexa-app/issues/1368)) ([f97a6f9](https://github.com/BLSQ/openhexa-app/commit/f97a6f9d2a0e6a761ad07c03a5fd01720d09912f))
* searchable workspaces in the org page + list/card view (PATHWAYS-882) ([#1383](https://github.com/BLSQ/openhexa-app/issues/1383)) ([5673861](https://github.com/BLSQ/openhexa-app/commit/56738619dbaec58bf2a1c0c6584e0a0408e243dc))


### Bug Fixes

* Allow workspaces DB host to be overridden ([#1377](https://github.com/BLSQ/openhexa-app/issues/1377)) ([632b961](https://github.com/BLSQ/openhexa-app/commit/632b96180ca3dbd10a4518919872953b38217d29))
* dataset view is constrained to the workspaces where the org admin is explicitly assigned (PATHWAYS-890) ([#1360](https://github.com/BLSQ/openhexa-app/issues/1360)) ([65f191d](https://github.com/BLSQ/openhexa-app/commit/65f191dac39cf49188aa38adfd080c76bdc5f7d9))
* hydration error on pipeline run page, time in srr is not equal to time in client (HEXA-1361) ([#1376](https://github.com/BLSQ/openhexa-app/issues/1376)) ([b1ca789](https://github.com/BLSQ/openhexa-app/commit/b1ca789801e9194c74ef804c136aff3aa03cccd5))
* prettier config and pretty all files in the repo (HEXA-1371) ([#1372](https://github.com/BLSQ/openhexa-app/issues/1372)) ([230af89](https://github.com/BLSQ/openhexa-app/commit/230af892461e163160c1d61380fffb9fbd6bc38f))
* too many workspaces in the invite for admin owners (PATHWAYS-940) ([#1386](https://github.com/BLSQ/openhexa-app/issues/1386)) ([18d5718](https://github.com/BLSQ/openhexa-app/commit/18d5718be98e31e0284eb3a6cc60c4cd35a86594))
* truncation of organization names and toast on success invitation (PATHWAYS-882) ([#1382](https://github.com/BLSQ/openhexa-app/issues/1382)) ([c725b6c](https://github.com/BLSQ/openhexa-app/commit/c725b6c57bbb9563198efa63c8156f341e2f2e5c))

## [2.3.5](https://github.com/BLSQ/openhexa-app/compare/2.3.4...2.3.5) (2025-09-18)


### Bug Fixes

* UI of the code editor is moving on file modification and error (HEXA-1365) ([#1369](https://github.com/BLSQ/openhexa-app/issues/1369)) ([71184fa](https://github.com/BLSQ/openhexa-app/commit/71184fa56450d6e11b16b7df22f3432cf152f327))

## [2.3.4](https://github.com/BLSQ/openhexa-app/compare/2.3.3...2.3.4) (2025-09-15)


### Bug Fixes

* viewing certain succeeded pipeline runs result in 500 errors (HEXA-1368) ([#1366](https://github.com/BLSQ/openhexa-app/issues/1366)) ([ed59dad](https://github.com/BLSQ/openhexa-app/commit/ed59dad40836bd893f52653fec850c88eaa76ae4))

## [2.3.3](https://github.com/BLSQ/openhexa-app/compare/2.3.2...2.3.3) (2025-09-15)


### Bug Fixes

* dataset link by slug should have a fallback to any of the dataset with the slug shared with the workspace (HEXA-1367) ([#1363](https://github.com/BLSQ/openhexa-app/issues/1363)) ([0d455ff](https://github.com/BLSQ/openhexa-app/commit/0d455ff3876cdbbc09827b5ef02b568bad1d1517))
* url of dataset when searching (PATHWAYS-895) ([#1361](https://github.com/BLSQ/openhexa-app/issues/1361)) ([a6966d6](https://github.com/BLSQ/openhexa-app/commit/a6966d6f0219937c77a972c0ba3dfe79433303c4))
* Viewing certain succeeded pipeline runs result in 500 errors (HEXA-1368) ([#1365](https://github.com/BLSQ/openhexa-app/issues/1365)) ([f8eb140](https://github.com/BLSQ/openhexa-app/commit/f8eb14078042959ef0bb7519b6a2b7685ffd454c))

## [2.3.2](https://github.com/BLSQ/openhexa-app/compare/2.3.1...2.3.2) (2025-09-11)


### Bug Fixes

* **deps:** update dependency express-http-proxy to v2.1.2 ([#1349](https://github.com/BLSQ/openhexa-app/issues/1349)) ([5af2eaf](https://github.com/BLSQ/openhexa-app/commit/5af2eaf9cf47c99ebad2729d67512cef81168c97))
* editing pipeline code in the browser should keep the parameters (HEXA-1364) ([#1358](https://github.com/BLSQ/openhexa-app/issues/1358)) ([770a018](https://github.com/BLSQ/openhexa-app/commit/770a0187bd3bbb37a6008c19383339f1bc0c74d8))
* File paths for folder creation and file upload ([#1359](https://github.com/BLSQ/openhexa-app/issues/1359)) ([55525fb](https://github.com/BLSQ/openhexa-app/commit/55525fbd9b0120125dd7aa4e9399911f60d4860d))

## [2.3.1](https://github.com/BLSQ/openhexa-app/compare/2.3.0...2.3.1) (2025-09-09)


### Bug Fixes

* Inconsistent behavior when dataset is published at the org level (PATHWAYS-888) ([#1351](https://github.com/BLSQ/openhexa-app/issues/1351)) ([a20249c](https://github.com/BLSQ/openhexa-app/commit/a20249c00bc1456b5fed411e774decb2c2e81f1b))

## [2.3.0](https://github.com/BLSQ/openhexa-app/compare/2.2.0...2.3.0) (2025-09-09)


### Features

* File browser parameter ([#1333](https://github.com/BLSQ/openhexa-app/issues/1333)) ([6c1e29d](https://github.com/BLSQ/openhexa-app/commit/6c1e29d440d9c0844638b80f49d8b1e43dc03460))


### Bug Fixes

* **deps:** update dependency @mdxeditor/editor to v3.43.0 ([#1345](https://github.com/BLSQ/openhexa-app/issues/1345)) ([a1cfcc7](https://github.com/BLSQ/openhexa-app/commit/a1cfcc7de9ec3e7d0af6423f184f90d871745c38))
* **deps:** update dependency i18next to v25.5.2 ([#1346](https://github.com/BLSQ/openhexa-app/issues/1346)) ([50af974](https://github.com/BLSQ/openhexa-app/commit/50af974bfed2f79482b2ae2435529537cd0a929e))
* **deps:** update nextjs monorepo to v15.5.2 ([#1341](https://github.com/BLSQ/openhexa-app/issues/1341)) ([2a63cd6](https://github.com/BLSQ/openhexa-app/commit/2a63cd6f4745065821fbfac15aa80082f140c602))

## [2.2.0](https://github.com/BLSQ/openhexa-app/compare/2.1.0...2.2.0) (2025-09-08)


### Features

* **organization:** F4 - Internal dataset governance (PATHWAYS-809, HEXA-1349) ([#1325](https://github.com/BLSQ/openhexa-app/issues/1325)) ([9bb3353](https://github.com/BLSQ/openhexa-app/commit/9bb3353ecc3dadc4d3a4d6157bfcb333eb891df6))
* **Organization:** list of all datasets in the organization landing page (PATHWAYS-866) ([#1326](https://github.com/BLSQ/openhexa-app/issues/1326)) ([9dd1940](https://github.com/BLSQ/openhexa-app/commit/9dd194096b71c9923b3f41d23aa14771dc9a516d))
* **pipelines:** update pipelines from template toggle PATHWAYS-635 ([#1324](https://github.com/BLSQ/openhexa-app/issues/1324)) ([e780f95](https://github.com/BLSQ/openhexa-app/commit/e780f95cf04d3b381a056c7f6ee27021536a03d0))


### Bug Fixes

* Admin and organization owners should have access to all workspaces in the organization (PATHWAYS-842) ([#1327](https://github.com/BLSQ/openhexa-app/issues/1327)) ([ae42512](https://github.com/BLSQ/openhexa-app/commit/ae425120c13b11403f3d892170415abd2a71c9eb))
* apollo deprecated config after dependency upgrade (HEXA-1357) ([#1337](https://github.com/BLSQ/openhexa-app/issues/1337)) ([ef46518](https://github.com/BLSQ/openhexa-app/commit/ef465189cf47fcb625a053a1e6a493f0706abe9b))
* **deps:** update dependency @apollo/client to v3.14.0 ([#1312](https://github.com/BLSQ/openhexa-app/issues/1312)) ([847692e](https://github.com/BLSQ/openhexa-app/commit/847692e2198d9d7bf931edfd05e5bdfe8cfe1371))
* **deps:** update dependency @types/node to v22.18.1 ([#1321](https://github.com/BLSQ/openhexa-app/issues/1321)) ([4efadb8](https://github.com/BLSQ/openhexa-app/commit/4efadb8965a6c3bd3c70d65b8bc18c41e3db7277))
* **deps:** update dependency @types/react to v18.3.24 ([#1317](https://github.com/BLSQ/openhexa-app/issues/1317)) ([d9e0211](https://github.com/BLSQ/openhexa-app/commit/d9e0211750c4f71f0297ba791ffef155d03f6658))
* **deps:** update dependency cron-parser to v5.3.1 ([#1334](https://github.com/BLSQ/openhexa-app/issues/1334)) ([8ddb3ce](https://github.com/BLSQ/openhexa-app/commit/8ddb3ce4c1a4222a7d3e0f0733dc038acc3c3656))
* **deps:** update dependency i18next to v25.4.2 ([#1318](https://github.com/BLSQ/openhexa-app/issues/1318)) ([bc743d3](https://github.com/BLSQ/openhexa-app/commit/bc743d3c0b23f0964b7708b3bb3283642cfb13ae))
* **deps:** update dependency luxon to v3.7.2 ([#1335](https://github.com/BLSQ/openhexa-app/issues/1335)) ([ab39637](https://github.com/BLSQ/openhexa-app/commit/ab3963768107f04692b184ec399fc30f5a7335bf))
* **deps:** update dependency react-i18next to v15.7.2 ([#1319](https://github.com/BLSQ/openhexa-app/issues/1319)) ([c198687](https://github.com/BLSQ/openhexa-app/commit/c19868702e9c4d443587e017b90deb8e4415fb46))
* **deps:** update dependency react-i18next to v15.7.3 ([#1340](https://github.com/BLSQ/openhexa-app/issues/1340)) ([89e65c0](https://github.com/BLSQ/openhexa-app/commit/89e65c05ef63365212fe835e581e6e594319dee3))
* **deps:** update dependency typescript to v5.9.2 ([#1309](https://github.com/BLSQ/openhexa-app/issues/1309)) ([cf33919](https://github.com/BLSQ/openhexa-app/commit/cf339193ff71ae74c94cf25ff528908b6ee3c133))
* **deps:** update nextjs monorepo to v15.5.0 ([#1310](https://github.com/BLSQ/openhexa-app/issues/1310)) ([666fa5f](https://github.com/BLSQ/openhexa-app/commit/666fa5f55b3aa40c6ae089789eac97d037fb518d))
* images in emails are not shown correctly, at least in gmail (HEXA-1351) ([#1328](https://github.com/BLSQ/openhexa-app/issues/1328)) ([3347c1e](https://github.com/BLSQ/openhexa-app/commit/3347c1e5d05d7c153e3e52b54af12d847ca61281))
* new org admin should have admin permissions on workspaces by default (PATHWAYS-879) ([#1329](https://github.com/BLSQ/openhexa-app/issues/1329)) ([b30a437](https://github.com/BLSQ/openhexa-app/commit/b30a43764bae5054c707f52ce97069089ff9c902))
* permissions and redirect when revoking access to a shared dataset (HEXA-1353) ([#1338](https://github.com/BLSQ/openhexa-app/issues/1338)) ([90d7bc6](https://github.com/BLSQ/openhexa-app/commit/90d7bc6d56f30e0b30de28d0a4aa23e726f41f1f))
* when inviting new users in the organization no suggestion should be made to prevent leaking users emails (PATHWAYS-843) ([#1336](https://github.com/BLSQ/openhexa-app/issues/1336)) ([d14c410](https://github.com/BLSQ/openhexa-app/commit/d14c41000b1949cfecbdcf13be4a0ec1aa4498a7))

## [2.1.0](https://github.com/BLSQ/openhexa-app/compare/2.0.0...2.1.0) (2025-08-21)


### Features

* workspace specific configuration (PATHWAYS-634 ) ([#1283](https://github.com/BLSQ/openhexa-app/issues/1283)) ([09cf074](https://github.com/BLSQ/openhexa-app/commit/09cf074972c1ba6e6caebf5cb417bec6e1c0a2c1))


### Bug Fixes

* **deps:** update dependency @mdxeditor/editor to v3.42.0 ([#1300](https://github.com/BLSQ/openhexa-app/issues/1300)) ([5760ad0](https://github.com/BLSQ/openhexa-app/commit/5760ad097860ac8194437f54062b1c7c5ce52349))
* **deps:** update dependency @types/node to v22.17.2 ([#1302](https://github.com/BLSQ/openhexa-app/issues/1302)) ([cdefe13](https://github.com/BLSQ/openhexa-app/commit/cdefe13da2718b5830161c7e6b3d6276185772ef))
* **deps:** update dependency @uiw/react-codemirror to v4.25.1 ([#1304](https://github.com/BLSQ/openhexa-app/issues/1304)) ([7e393af](https://github.com/BLSQ/openhexa-app/commit/7e393af30eb0c6c0abf28024fb7373f54c0d3c4d))
* **deps:** update dependency i18next to v25.4.0 ([#1306](https://github.com/BLSQ/openhexa-app/issues/1306)) ([2e10075](https://github.com/BLSQ/openhexa-app/commit/2e10075c2bf2657f3f9db57c8522ddaa2c40dd13))
* **deps:** update dependency react-i18next to v15.7.1 ([#1307](https://github.com/BLSQ/openhexa-app/issues/1307)) ([f80f9d9](https://github.com/BLSQ/openhexa-app/commit/f80f9d9484a20feae03a0306973db6f4e42a7c3c))
* UI organization issues (PATHWAYS-834) ([#1308](https://github.com/BLSQ/openhexa-app/issues/1308)) ([0c672d1](https://github.com/BLSQ/openhexa-app/commit/0c672d1686f52dc7ecfc0d82002f6deb8799df63))

## [2.0.0](https://github.com/BLSQ/openhexa-app/compare/1.14.0...2.0.0) (2025-08-20)


### ⚠ BREAKING CHANGES

* Manage users at the Organization level (PATHWAYS-631) ([#1272](https://github.com/BLSQ/openhexa-app/issues/1272))

### Features

* edit pipeline Python code from the UI  🎉 (HEXA-1341) ([#1278](https://github.com/BLSQ/openhexa-app/issues/1278)) ([fc4c77d](https://github.com/BLSQ/openhexa-app/commit/fc4c77d2f7669b5f9479a3577a9071e1c84cfa0c))
* Manage users at the Organization level (PATHWAYS-631) ([#1272](https://github.com/BLSQ/openhexa-app/issues/1272)) ([85dfac9](https://github.com/BLSQ/openhexa-app/commit/85dfac9d5028b30adf0415a64b64d104a05cde21))


### Bug Fixes

* **dataset:** wraps long filename to display download button, PATHWAYS-754 ([#1279](https://github.com/BLSQ/openhexa-app/issues/1279)) ([70511fa](https://github.com/BLSQ/openhexa-app/commit/70511faa4c458ba7cb1669add2a4d413ce657429))
* **deps:** update dependency @apollo/client to v3.13.9 ([#1292](https://github.com/BLSQ/openhexa-app/issues/1292)) ([2cb70ff](https://github.com/BLSQ/openhexa-app/commit/2cb70fffd9a00ee08a5ae8bc03f09f714cd4009d))
* **deps:** update dependency @headlessui/react to v2.2.7 ([#1293](https://github.com/BLSQ/openhexa-app/issues/1293)) ([6c4e0e0](https://github.com/BLSQ/openhexa-app/commit/6c4e0e0361114889a5918f94f0de9cd0a01bbc1d))
* **deps:** update dependency @sentry/nextjs to v9.46.0 ([#1267](https://github.com/BLSQ/openhexa-app/issues/1267)) ([f0e21c6](https://github.com/BLSQ/openhexa-app/commit/f0e21c6a93a57e6c8d8f7ad8323f22725a7274d4))
* **deps:** update dependency cookies-next to v6.1.0 ([#1268](https://github.com/BLSQ/openhexa-app/issues/1268)) ([4c12e3d](https://github.com/BLSQ/openhexa-app/commit/4c12e3d447b426d831d63aecf9bd88695598cf20))
* **deps:** update dependency i18next to v25.3.6 ([#1294](https://github.com/BLSQ/openhexa-app/issues/1294)) ([5dccfd6](https://github.com/BLSQ/openhexa-app/commit/5dccfd6c31705df56621f423416f2b46483f06c1))
* **deps:** update dependency linkify-react to v4.3.2 ([#1295](https://github.com/BLSQ/openhexa-app/issues/1295)) ([2a040d9](https://github.com/BLSQ/openhexa-app/commit/2a040d9a23910549a1863634754024cb9fd21bcf))
* **deps:** update dependency luxon to v3.7.1 ([#1270](https://github.com/BLSQ/openhexa-app/issues/1270)) ([4e18dc2](https://github.com/BLSQ/openhexa-app/commit/4e18dc2bc1e95ae666ca44f3e4dc93f6f13df8ed))
* **deps:** update dependency react-i18next to v15.6.1 ([#1271](https://github.com/BLSQ/openhexa-app/issues/1271)) ([8e1f6bb](https://github.com/BLSQ/openhexa-app/commit/8e1f6bbbaa7377c38b646991e83ea399d21bca80))
* **deps:** update graphqlcodegenerator monorepo ([#1185](https://github.com/BLSQ/openhexa-app/issues/1185)) ([5bbbbf8](https://github.com/BLSQ/openhexa-app/commit/5bbbbf8bc349b984cf3291b0ab6c0437b0ae1e33))
* Minor improvements to Pipeline Templates UI and Admin (HEXA-1338, HEXA-1339, HEXA-1340) ([#1276](https://github.com/BLSQ/openhexa-app/issues/1276)) ([e3828c9](https://github.com/BLSQ/openhexa-app/commit/e3828c9102c5c82398a09c71d07f193517d90487))

## [1.14.0](https://github.com/BLSQ/openhexa-app/compare/1.13.0...1.14.0) (2025-07-17)


### Features

* as a user i want to view the code of the template (HEXA-1309) ([#1254](https://github.com/BLSQ/openhexa-app/issues/1254)) ([22e2bb0](https://github.com/BLSQ/openhexa-app/commit/22e2bb0ce6298514ccf343b71baf875877cbd634))


### Bug Fixes

* add paging to dataset files (HEXA-1329 ) ([#1241](https://github.com/BLSQ/openhexa-app/issues/1241)) ([c3ee15e](https://github.com/BLSQ/openhexa-app/commit/c3ee15e1a9bf3f27b3bf0145869cc5d911f20d8b))
* Allow Superset dashboard in web apps ([#1264](https://github.com/BLSQ/openhexa-app/issues/1264)) ([be2c1ef](https://github.com/BLSQ/openhexa-app/commit/be2c1ef0f73a8f626c337228e643d50d3936df2e))
* codegen generation issue  ([#1253](https://github.com/BLSQ/openhexa-app/issues/1253)) ([902c3bb](https://github.com/BLSQ/openhexa-app/commit/902c3bb48da1fcd2d7f48985d3afe1884ba2a820))
* **deps:** update dependency @mdxeditor/editor to v3.39.1 ([#1257](https://github.com/BLSQ/openhexa-app/issues/1257)) ([e11090d](https://github.com/BLSQ/openhexa-app/commit/e11090d59ccc1047862ade11ddb9040ab196f321))
* **deps:** update dependency @sentry/nextjs to v9.38.0 ([#1258](https://github.com/BLSQ/openhexa-app/issues/1258)) ([84464cb](https://github.com/BLSQ/openhexa-app/commit/84464cbcf877a2596cdada23d67e60abe0bc7e6f))
* **deps:** update dependency @types/node to v22.16.3 ([#1259](https://github.com/BLSQ/openhexa-app/issues/1259)) ([9753d12](https://github.com/BLSQ/openhexa-app/commit/9753d1223d596bdf98912f015e635b2285a6fc24))
* **deps:** update dependency @types/node to v22.16.4 ([#1266](https://github.com/BLSQ/openhexa-app/issues/1266)) ([f0730f4](https://github.com/BLSQ/openhexa-app/commit/f0730f4ae70a1eec5d572538fa18f8023af25634))
* **deps:** update dependency @uiw/react-codemirror to v4.24.1 ([#1261](https://github.com/BLSQ/openhexa-app/issues/1261)) ([86fcebf](https://github.com/BLSQ/openhexa-app/commit/86fcebf8e0abf39c1f34b588dc6b4e6f96b2558b))
* **deps:** update dependency dotenv to v16.6.1 ([#1262](https://github.com/BLSQ/openhexa-app/issues/1262)) ([0dc8ac8](https://github.com/BLSQ/openhexa-app/commit/0dc8ac8278638013709b434bf5611058eee7281c))
* **deps:** update dependency i18next to v25.3.2 ([#1263](https://github.com/BLSQ/openhexa-app/issues/1263)) ([2838c64](https://github.com/BLSQ/openhexa-app/commit/2838c641400370eec19a009eea8c032d705a625a))
* **deps:** update jest monorepo to v30 (major) ([#1209](https://github.com/BLSQ/openhexa-app/issues/1209)) ([50ebd48](https://github.com/BLSQ/openhexa-app/commit/50ebd486454bbbbb5c116dd8090e66cd921d8d3a))
* exposes pipeline code in kubernetes ([#1251](https://github.com/BLSQ/openhexa-app/issues/1251)) ([adc3199](https://github.com/BLSQ/openhexa-app/commit/adc319917811c507787b890a0f96f8e91e87b4e8))

## [1.13.0](https://github.com/BLSQ/openhexa-app/compare/1.12.1...1.13.0) (2025-07-09)


### Features

* View pipeline code (HEXA-1302) ([#1239](https://github.com/BLSQ/openhexa-app/issues/1239)) ([cb37aa3](https://github.com/BLSQ/openhexa-app/commit/cb37aa3b3bdba7f0872915629538b3fd675d8dcb))


### Bug Fixes

* **deps:** update nextjs monorepo to v15.3.5 ([#1244](https://github.com/BLSQ/openhexa-app/issues/1244)) ([6e1427b](https://github.com/BLSQ/openhexa-app/commit/6e1427b93071cfd065538a815d39414ffb852916))

## [1.12.1](https://github.com/BLSQ/openhexa-app/compare/1.12.0...1.12.1) (2025-07-08)


### Bug Fixes

* Allow OpenHEXA to embed itself, needed for Superset dashboard in Web Apps ([d0f1a63](https://github.com/BLSQ/openhexa-app/commit/d0f1a632b30d6210b93e8340f1ad569c162704e7))
* **deps:** update dependency @types/lodash to v4.17.20 ([#1243](https://github.com/BLSQ/openhexa-app/issues/1243)) ([d734113](https://github.com/BLSQ/openhexa-app/commit/d7341130c99c1fa21f6063281a6b1645b9d309a4))
* filter for user methods to support pipeline token for most methods (HEXA-1316 ) ([#1237](https://github.com/BLSQ/openhexa-app/issues/1237)) ([5fc18ec](https://github.com/BLSQ/openhexa-app/commit/5fc18ecf81dd2a7db8e0e2c72ba1641efed3177c))

## [1.12.0](https://github.com/BLSQ/openhexa-app/compare/1.11.0...1.12.0) (2025-06-30)


### Features

* F1 organizations landing page (PATHWAYS-557) ([#1190](https://github.com/BLSQ/openhexa-app/issues/1190)) ([f1b2d1c](https://github.com/BLSQ/openhexa-app/commit/f1b2d1c930db66d20cac8138c8d4052b919b26b4))
* F2 organization workspaces management (PATHWAYS-577) ([#1212](https://github.com/BLSQ/openhexa-app/issues/1212)) ([8dfd87a](https://github.com/BLSQ/openhexa-app/commit/8dfd87a5c4fcd0a58ae65cddb1fd6537a499fbc8))


### Bug Fixes

* click outside search bar ([#1210](https://github.com/BLSQ/openhexa-app/issues/1210)) ([37b90db](https://github.com/BLSQ/openhexa-app/commit/37b90db69543e3e1f699830170e9e6fc755a3f8c))
* **deps:** update dependency @codemirror/lang-json to v6.0.2 ([#1221](https://github.com/BLSQ/openhexa-app/issues/1221)) ([83501b9](https://github.com/BLSQ/openhexa-app/commit/83501b9e04f7ad17edb7c77d571e0d699a8bde69))
* **deps:** update dependency @mdxeditor/editor to v3.35.1 ([#1204](https://github.com/BLSQ/openhexa-app/issues/1204)) ([b25a457](https://github.com/BLSQ/openhexa-app/commit/b25a457cc4c86a201d136e00dd78ba02003d14c1))
* **deps:** update dependency @sentry/nextjs to v9.31.0 ([#1195](https://github.com/BLSQ/openhexa-app/issues/1195)) ([ba192fe](https://github.com/BLSQ/openhexa-app/commit/ba192febfd3c2f457c25259b97edb5dab33d0824))
* **deps:** update dependency @types/lodash to v4.17.19 ([#1222](https://github.com/BLSQ/openhexa-app/issues/1222)) ([dd6c31e](https://github.com/BLSQ/openhexa-app/commit/dd6c31e231144280c9dc6d8d156eda993fb9d70c))
* **deps:** update dependency @types/node to v22.15.31 ([#1207](https://github.com/BLSQ/openhexa-app/issues/1207)) ([9bb69b9](https://github.com/BLSQ/openhexa-app/commit/9bb69b9b249716ed5b9340bea4babdd4936db3fe))
* **deps:** update dependency @types/node to v22.15.33 ([#1224](https://github.com/BLSQ/openhexa-app/issues/1224)) ([80b3648](https://github.com/BLSQ/openhexa-app/commit/80b36489feb00286139651572989dcd79ea7a15b))
* **deps:** update dependency @types/node to v22.15.34 ([#1234](https://github.com/BLSQ/openhexa-app/issues/1234)) ([b6df484](https://github.com/BLSQ/openhexa-app/commit/b6df48477fa5004c1d0f10c637ca01afdded994e))
* **deps:** update dependency @uiw/react-codemirror to v4.23.13 ([#1208](https://github.com/BLSQ/openhexa-app/issues/1208)) ([00cce5b](https://github.com/BLSQ/openhexa-app/commit/00cce5b0ba59f64485e543dd6d7ae95ee55ce746))
* **deps:** update dependency @uiw/react-codemirror to v4.23.14 ([#1225](https://github.com/BLSQ/openhexa-app/issues/1225)) ([f14b831](https://github.com/BLSQ/openhexa-app/commit/f14b8310a594160bee4c15126b110a4601b589b8))
* **deps:** update dependency codemirror to v6.0.2 ([#1227](https://github.com/BLSQ/openhexa-app/issues/1227)) ([c38d25a](https://github.com/BLSQ/openhexa-app/commit/c38d25abfe92678c27eb37e01973536ad73f5bad))
* **deps:** update dependency cron-parser to v5.3.0 ([#1198](https://github.com/BLSQ/openhexa-app/issues/1198)) ([ee7c88e](https://github.com/BLSQ/openhexa-app/commit/ee7c88ed6aa6ca98a78054b5ce0ac620794be56b))
* **deps:** update dependency react-i18next to v15.5.3 ([#1228](https://github.com/BLSQ/openhexa-app/issues/1228)) ([76d671d](https://github.com/BLSQ/openhexa-app/commit/76d671d2d52c0516f6549a407cb307ca30d8b8eb))
* **deps:** update nextjs monorepo to v15.3.4 ([#1229](https://github.com/BLSQ/openhexa-app/issues/1229)) ([7816e11](https://github.com/BLSQ/openhexa-app/commit/7816e11e797e74b827dae3c3d2e71d6d76e0e674))
* New user invitation flow: fix small glitch and remove feature flag (HEXA-1296) ([b194a44](https://github.com/BLSQ/openhexa-app/commit/b194a44cc499c2cbddddf34ea4bf7446293c0cc4))

## [1.11.0](https://github.com/BLSQ/openhexa-app/compare/1.10.0...1.11.0) (2025-06-10)


### Features

* cleaner email invitation for existing ([#1187](https://github.com/BLSQ/openhexa-app/issues/1187)) ([d77d5cf](https://github.com/BLSQ/openhexa-app/commit/d77d5cf39f03b2d87cd452e7062a2908e671e7b1))


### Bug Fixes

* **deps:** update dependency @types/node to v22.15.30 ([#1189](https://github.com/BLSQ/openhexa-app/issues/1189)) ([a02eda9](https://github.com/BLSQ/openhexa-app/commit/a02eda9897d104e203fc9174f0caeda6d1df5f50))
* searching when changing page of results & UI glitch caused by z-index (HEXA-1293) ([#1200](https://github.com/BLSQ/openhexa-app/issues/1200)) ([ee79240](https://github.com/BLSQ/openhexa-app/commit/ee792401920a69b66dbc65e9013ff3440ba5ac5c))

## [1.10.0](https://github.com/BLSQ/openhexa-app/compare/1.9.1...1.10.0) (2025-06-05)


### Features

* Enable search bar by removing feature flag ([#1182](https://github.com/BLSQ/openhexa-app/issues/1182)) ([dc27321](https://github.com/BLSQ/openhexa-app/commit/dc273217a3f88767330ca043785dbc20149b4043))
* removed promotion content from email template ([#1179](https://github.com/BLSQ/openhexa-app/issues/1179)) ([50c07b5](https://github.com/BLSQ/openhexa-app/commit/50c07b537715adfaa00d31a35d835f2a585df426))


### Bug Fixes

* **deps:** update dependency @mdxeditor/editor to v3.35.0 ([#1172](https://github.com/BLSQ/openhexa-app/issues/1172)) ([626d390](https://github.com/BLSQ/openhexa-app/commit/626d3904315d66058832f0db2f6c36b6bd23e856))
* **deps:** update dependency @sentry/nextjs to v9.26.0 ([#1173](https://github.com/BLSQ/openhexa-app/issues/1173)) ([5444bf6](https://github.com/BLSQ/openhexa-app/commit/5444bf628a796f84e9c8c4889c296777c18e6030))
* **deps:** update dependency cookies-next to v6 ([#1175](https://github.com/BLSQ/openhexa-app/issues/1175)) ([2cec3dc](https://github.com/BLSQ/openhexa-app/commit/2cec3dccc0ecff9acd5237ea30b49257b57e5ad1))
* progress overlay ([#1183](https://github.com/BLSQ/openhexa-app/issues/1183)) ([96d2aa8](https://github.com/BLSQ/openhexa-app/commit/96d2aa84e86b1ad9ae196e162ba275735ad2a0e2))
* User search query not working on add member to workspace modal ([#1180](https://github.com/BLSQ/openhexa-app/issues/1180)) ([9bc1f38](https://github.com/BLSQ/openhexa-app/commit/9bc1f380d62c97003e764924741b0f7486556eb8))

## [1.9.1](https://github.com/BLSQ/openhexa-app/compare/1.9.0...1.9.1) (2025-06-03)


### Bug Fixes

* Add notebooks_server_hash and access_token to migration ([#1162](https://github.com/BLSQ/openhexa-app/issues/1162)) ([1d4ee4c](https://github.com/BLSQ/openhexa-app/commit/1d4ee4cf94f0d41a409bd85737100d5983f8035e))
* **deps:** update dependency @types/node to v22.15.29 ([#1168](https://github.com/BLSQ/openhexa-app/issues/1168)) ([de780a9](https://github.com/BLSQ/openhexa-app/commit/de780a9606f1cdad8f5cb33b353aec2b3b562489))
* **deps:** update nextjs monorepo to v15.3.3 ([#1170](https://github.com/BLSQ/openhexa-app/issues/1170)) ([c255c2e](https://github.com/BLSQ/openhexa-app/commit/c255c2e01644293be2a7d12e8be7970fb0733ccb))
* HEXA-1283 Remove deprecated `requiredStatusChecks`... ([#1176](https://github.com/BLSQ/openhexa-app/issues/1176)) ([0921aa2](https://github.com/BLSQ/openhexa-app/commit/0921aa274412acbaa8214f70463fe6cd9820dc09))
* revert "chore(deps): update graphqlcodegenerator monorepo ([#1165](https://github.com/BLSQ/openhexa-app/issues/1165))" ([#1177](https://github.com/BLSQ/openhexa-app/issues/1177)) ([1b205ca](https://github.com/BLSQ/openhexa-app/commit/1b205ca79e37526608047a4643e9cbdef64fd928))

## [1.9.0](https://github.com/BLSQ/openhexa-app/compare/1.8.2...1.9.0) (2025-06-02)


### Features

* add the source workspace in the template selection table (HEXA-1285 ) ([#1158](https://github.com/BLSQ/openhexa-app/issues/1158)) ([d15adaa](https://github.com/BLSQ/openhexa-app/commit/d15adaa320af91f26fe94d7139bb91cc8955c751))
* Simplify flow of adding/inviting members to workspaces ([#1123](https://github.com/BLSQ/openhexa-app/issues/1123)) ([d258052](https://github.com/BLSQ/openhexa-app/commit/d258052d60c7666e2b34c7fdda2729fbef3fbef4))


### Bug Fixes

* **deps:** update dependency @types/node to v22.15.23 ([#1152](https://github.com/BLSQ/openhexa-app/issues/1152)) ([63ae610](https://github.com/BLSQ/openhexa-app/commit/63ae61079bd2b806c91e2e061bb7549ff81a4495))
* **deps:** update dependency @types/react to v18.3.23 ([#1153](https://github.com/BLSQ/openhexa-app/issues/1153)) ([3f0b496](https://github.com/BLSQ/openhexa-app/commit/3f0b496ea4373f9c5327e7e967ff8092c31a323d))
* **deps:** update dependency i18next to v25.2.1 ([#1156](https://github.com/BLSQ/openhexa-app/issues/1156)) ([984d2b3](https://github.com/BLSQ/openhexa-app/commit/984d2b37c91510467800674a86af520bfdf13466))
* **deps:** update dependency react-hotkeys-hook to v5.1.0 ([#1147](https://github.com/BLSQ/openhexa-app/issues/1147)) ([173645a](https://github.com/BLSQ/openhexa-app/commit/173645a484cf706d8d51e97a7f420f07a1259164))
* **deps:** update linkifyjs monorepo to v4.3.1 ([#1148](https://github.com/BLSQ/openhexa-app/issues/1148)) ([00be4d7](https://github.com/BLSQ/openhexa-app/commit/00be4d71351c288fe262a7760963ca2b13ceff4d))
* overlay progress on initial page load ([#1144](https://github.com/BLSQ/openhexa-app/issues/1144)) ([b9e5e03](https://github.com/BLSQ/openhexa-app/commit/b9e5e03ea9b541cd18c2c35101b0381a8a46e198))
* revert codegen dependency upgrade ([#1159](https://github.com/BLSQ/openhexa-app/issues/1159)) ([f4fa37a](https://github.com/BLSQ/openhexa-app/commit/f4fa37a97728abb7f9d7340b9523d69f9e3a2db6))

## [1.8.2](https://github.com/BLSQ/openhexa-app/compare/1.8.1...1.8.2) (2025-05-23)


### Bug Fixes

* **deps:** update dependency react-i18next to v15.5.2 ([#1142](https://github.com/BLSQ/openhexa-app/issues/1142)) ([228fa2c](https://github.com/BLSQ/openhexa-app/commit/228fa2ce3ca0864c7725a899f21a256bdb0f2ad8))
* ignore hidden files in path of GCP (HEXA-1279) ([#1140](https://github.com/BLSQ/openhexa-app/issues/1140)) ([e172d14](https://github.com/BLSQ/openhexa-app/commit/e172d14cce3246925cec3b1c9eb481808ba9c770))

## [1.8.1](https://github.com/BLSQ/openhexa-app/compare/1.8.0...1.8.1) (2025-05-23)


### Bug Fixes

* **deps:** update dependency @headlessui/react to v2.2.4 ([#1135](https://github.com/BLSQ/openhexa-app/issues/1135)) ([5f57137](https://github.com/BLSQ/openhexa-app/commit/5f57137fdc3a3c46ce237ec954b6ab507d5b5400))
* **deps:** update dependency @types/lodash to v4.17.17 ([#1137](https://github.com/BLSQ/openhexa-app/issues/1137)) ([96fcad3](https://github.com/BLSQ/openhexa-app/commit/96fcad3772e71e9d52e5a5e56596baa9130fb997))
* **deps:** update dependency @types/node to v22.15.21 ([#1138](https://github.com/BLSQ/openhexa-app/issues/1138)) ([20e7bf5](https://github.com/BLSQ/openhexa-app/commit/20e7bf5d1d66ffd30ae37b868fa6d828a1a22178))
* **deps:** update dependency @types/react to v18.3.22 ([#1139](https://github.com/BLSQ/openhexa-app/issues/1139)) ([dccba39](https://github.com/BLSQ/openhexa-app/commit/dccba3931a3dd2f81be070586c96c80c31debfbc))
* ignore hidden files ([#1132](https://github.com/BLSQ/openhexa-app/issues/1132)) ([dbe0906](https://github.com/BLSQ/openhexa-app/commit/dbe09064be8e16f13a7a081e73645c055781504e))

## [1.8.0](https://github.com/BLSQ/openhexa-app/compare/1.7.1...1.8.0) (2025-05-22)


### Features

* remove dataset smart previewer feature flag (HEXA-1277) ([#1127](https://github.com/BLSQ/openhexa-app/issues/1127)) ([fbae842](https://github.com/BLSQ/openhexa-app/commit/fbae842d016c2e215d9845a0bbf5ca9d993f49e9))
* search bar UI improvements (HEXA-1276) ([#1129](https://github.com/BLSQ/openhexa-app/issues/1129)) ([85a0e0c](https://github.com/BLSQ/openhexa-app/commit/85a0e0cddd4e9ecff4ed340ae41827933d0b1227))


### Bug Fixes

* **deps:** update dependency @sentry/nextjs to v9.22.0 ([#1099](https://github.com/BLSQ/openhexa-app/issues/1099)) ([cd18d79](https://github.com/BLSQ/openhexa-app/commit/cd18d79c4ff98b73998456129da3d38618d8d7ad))
* **deps:** update dependency cron-parser to v5.2.0 ([#1100](https://github.com/BLSQ/openhexa-app/issues/1100)) ([37b8b2e](https://github.com/BLSQ/openhexa-app/commit/37b8b2ee08134e72f4b051077a5c2198afd78702))
* **deps:** update dependency cronstrue to v2.61.0 ([#1101](https://github.com/BLSQ/openhexa-app/issues/1101)) ([e05cc52](https://github.com/BLSQ/openhexa-app/commit/e05cc528aff4e0975680982f806578098e8fc91f))
* **deps:** update dependency i18next to v25.2.0 ([#1102](https://github.com/BLSQ/openhexa-app/issues/1102)) ([0ec155b](https://github.com/BLSQ/openhexa-app/commit/0ec155b5f7f8a134adc1905fabcb1c3bc742891e))
* profiling and sampling issue with infinity (HEXA-1278) ([#1126](https://github.com/BLSQ/openhexa-app/issues/1126)) ([2921abf](https://github.com/BLSQ/openhexa-app/commit/2921abfcce71f010e783625c003784fbff238ed3))

## [1.7.1](https://github.com/BLSQ/openhexa-app/compare/1.7.0...1.7.1) (2025-05-19)


### Bug Fixes

* file profiling is failing for only one cell in a column (HEXA-1275) ([#1124](https://github.com/BLSQ/openhexa-app/issues/1124)) ([884c468](https://github.com/BLSQ/openhexa-app/commit/884c468dd261b7e6e8b4d2135b662db26a8f70eb))

## [1.7.0](https://github.com/BLSQ/openhexa-app/compare/1.6.4...1.7.0) (2025-05-15)


### Features

* add last run status to pipeline grid view (HEXA-1268) ([#1121](https://github.com/BLSQ/openhexa-app/issues/1121)) ([fc63258](https://github.com/BLSQ/openhexa-app/commit/fc632582ba9c76648ba11ba18a47a619501ff013))


### Bug Fixes

* search bar flickering on scroll due to on hover styles (HEXA-1267) ([#1119](https://github.com/BLSQ/openhexa-app/issues/1119)) ([0e1d52c](https://github.com/BLSQ/openhexa-app/commit/0e1d52cf6b4a66867f96906081bcca929e9c5e88))

## [1.6.4](https://github.com/BLSQ/openhexa-app/compare/1.6.3...1.6.4) (2025-05-14)


### Bug Fixes

* **deps:** update dependency @types/node to v22.15.18 ([#1115](https://github.com/BLSQ/openhexa-app/issues/1115)) ([0eeb9fa](https://github.com/BLSQ/openhexa-app/commit/0eeb9fa50d2b3ca1641baae193dde814cf79ec44))
* Search bar : long name needs to be clamped, results scrollable (HEXA-1265) ([#1118](https://github.com/BLSQ/openhexa-app/issues/1118)) ([e91ab05](https://github.com/BLSQ/openhexa-app/commit/e91ab0510d238ab5077591988633c2ceb2dbaa50))

## [1.6.3](https://github.com/BLSQ/openhexa-app/compare/1.6.2...1.6.3) (2025-05-14)


### Bug Fixes

* Caching and SRR of pipelines (HEXA-1262) ([#1109](https://github.com/BLSQ/openhexa-app/issues/1109)) ([4621ad4](https://github.com/BLSQ/openhexa-app/commit/4621ad42a597dde4bb1ea0a88f22d19d0cc3c617))
* **deps:** update dependency @codemirror/lang-python to v6.2.1 ([#1112](https://github.com/BLSQ/openhexa-app/issues/1112)) ([ba08e59](https://github.com/BLSQ/openhexa-app/commit/ba08e597782bccb3e17fd991312a77432c5889d6))
* **deps:** update dependency @headlessui/react to v2.2.3 ([#1113](https://github.com/BLSQ/openhexa-app/issues/1113)) ([14a47ae](https://github.com/BLSQ/openhexa-app/commit/14a47aeced94033755b273f255d08afe28faaa6e))
* **deps:** update dependency @mdxeditor/editor to v3.32.3 ([#1114](https://github.com/BLSQ/openhexa-app/issues/1114)) ([91e5e95](https://github.com/BLSQ/openhexa-app/commit/91e5e95cffb708120d0078ad4f2b2027f022ff09))
* **superset:** Add missing view in the anonymous routes ([#1108](https://github.com/BLSQ/openhexa-app/issues/1108)) ([6f7ecf1](https://github.com/BLSQ/openhexa-app/commit/6f7ecf1d1e9e3bb51852b1a520aac8951c45abea))
* **tests:** Update jest snapshots ([c5189fc](https://github.com/BLSQ/openhexa-app/commit/c5189fc198c770221d462c24799eaf0d09004b58))
* The name of the latest version of a dataset cannot be edited (HEXA-1257) ([#1106](https://github.com/BLSQ/openhexa-app/issues/1106)) ([d428861](https://github.com/BLSQ/openhexa-app/commit/d428861c166c4fd2745e8568d0120656d44e7a67))
* web hook toggle can be changed while not in edit mode (HEXA-1264) ([#1110](https://github.com/BLSQ/openhexa-app/issues/1110)) ([9a3f195](https://github.com/BLSQ/openhexa-app/commit/9a3f195c49973f032cc2e47b445ac75574a6acbf))

## [1.6.2](https://github.com/BLSQ/openhexa-app/compare/1.6.1...1.6.2) (2025-05-13)


### Bug Fixes

* search bar, navigating to templates can fail because the user is not member of the workspace (HEXA-1261) ([#1104](https://github.com/BLSQ/openhexa-app/issues/1104)) ([4fc78ba](https://github.com/BLSQ/openhexa-app/commit/4fc78ba14ba72b8dbeb808bdb314579ef77a8945))

## [1.6.1](https://github.com/BLSQ/openhexa-app/compare/1.6.0...1.6.1) (2025-05-12)


### Bug Fixes

* Tailwind upgrade to &gt; 4.1.4 is breaking the backdrop of dialog (HEXA-1258) ([#1097](https://github.com/BLSQ/openhexa-app/issues/1097)) ([c2fa80d](https://github.com/BLSQ/openhexa-app/commit/c2fa80df08ef265896160adbf543c9d99e4dced6))

## [1.6.0](https://github.com/BLSQ/openhexa-app/compare/1.5.0...1.6.0) (2025-05-12)


### Features

* search bar (HEXA-1232, HEXA-1246) ([#1030](https://github.com/BLSQ/openhexa-app/issues/1030)) ([b3832c5](https://github.com/BLSQ/openhexa-app/commit/b3832c52cb4d7de03c158cc244d3f7860494feaa))


### Bug Fixes

* **deps:** update dependency @types/react to v18.3.21 ([#1082](https://github.com/BLSQ/openhexa-app/issues/1082)) ([197a8a4](https://github.com/BLSQ/openhexa-app/commit/197a8a4121a6c4fb8183b2881a80761f266a60f6))
* **deps:** update dependency @uiw/react-codemirror to v4.23.12 ([#1085](https://github.com/BLSQ/openhexa-app/issues/1085)) ([783901e](https://github.com/BLSQ/openhexa-app/commit/783901e9de618cd187bd845582b58be859f756dd))
* **deps:** update nextjs monorepo to v15.3.2 ([#1086](https://github.com/BLSQ/openhexa-app/issues/1086)) ([1683d25](https://github.com/BLSQ/openhexa-app/commit/1683d25fbce574b529aa272165af003cb6925493))

## [1.5.0](https://github.com/BLSQ/openhexa-app/compare/1.4.0...1.5.0) (2025-05-08)


### Features

* as a user i want to see summary stats of the numeric columns (PATHWAYS-313)  ([#1067](https://github.com/BLSQ/openhexa-app/issues/1067)) ([f0db51c](https://github.com/BLSQ/openhexa-app/commit/f0db51c6c04d93a73f56ed20692d5ed9e10560ab))
* list view of pipelines like for templates (HEXA-1247) ([#1066](https://github.com/BLSQ/openhexa-app/issues/1066)) ([d0f3753](https://github.com/BLSQ/openhexa-app/commit/d0f3753fa8597f7c8e918de3bbe9b52e756dc28d))


### Bug Fixes

* **deps:** update dependency @mdxeditor/editor to v3.32.2 ([#1060](https://github.com/BLSQ/openhexa-app/issues/1060)) ([3e677d7](https://github.com/BLSQ/openhexa-app/commit/3e677d7f1e044a0f1f7e5525f76bd4c964679e7c))
* **deps:** update dependency @sentry/nextjs to v9.16.1 ([#1062](https://github.com/BLSQ/openhexa-app/issues/1062)) ([94c7f0d](https://github.com/BLSQ/openhexa-app/commit/94c7f0d0ba1197d4a89c64dd67a3761dfbf9831b))
* **deps:** update dependency @types/node to v22.15.16 ([#1064](https://github.com/BLSQ/openhexa-app/issues/1064)) ([022e295](https://github.com/BLSQ/openhexa-app/commit/022e2955f27ced3282dbe2a818d3a7986920172f))
* **deps:** update dependency @types/node to v22.15.17 ([#1079](https://github.com/BLSQ/openhexa-app/issues/1079)) ([78f0907](https://github.com/BLSQ/openhexa-app/commit/78f0907baaae13d91f51ac37f4112e9cbfa936ae))
* **deps:** update dependency graphql to v16.11.0 ([#1065](https://github.com/BLSQ/openhexa-app/issues/1065)) ([78d5623](https://github.com/BLSQ/openhexa-app/commit/78d5623fd2e76948ae85aac2c2dad0150bb3ac11))
* Set uid & gid to 1000 by default ([#1070](https://github.com/BLSQ/openhexa-app/issues/1070)) ([c9971c0](https://github.com/BLSQ/openhexa-app/commit/c9971c0b6717e7ffaee0625f2ccfc7c459f9705a))

## [1.4.0](https://github.com/BLSQ/openhexa-app/compare/1.3.0...1.4.0) (2025-04-29)


### Features

* **email:** enhance email sending functionality with attachments and update email template to use inline images ([#1057](https://github.com/BLSQ/openhexa-app/issues/1057)) ([cd317eb](https://github.com/BLSQ/openhexa-app/commit/cd317ebd21c9cac5d8cdc9c8f938d67ef41873a8))


### Bug Fixes

* **deps:** update dependency @codemirror/lang-python to v6.2.0 ([#1056](https://github.com/BLSQ/openhexa-app/issues/1056)) ([743ccbb](https://github.com/BLSQ/openhexa-app/commit/743ccbb271d395877e157275026fb006b028a25a))
* **deps:** update dependency @uiw/react-codemirror to v4.23.11 ([#1054](https://github.com/BLSQ/openhexa-app/issues/1054)) ([cba2bf1](https://github.com/BLSQ/openhexa-app/commit/cba2bf13cbc3c4ccc8e4c4d3ebe4db2b0318117b))
* **deps:** update dependency i18next to v25.0.2 ([#1059](https://github.com/BLSQ/openhexa-app/issues/1059)) ([d531fe7](https://github.com/BLSQ/openhexa-app/commit/d531fe70594fd604e67707ea8fca3a478e23cea5))
* **deps:** update dependency react-i18next to v15.5.1 ([#1052](https://github.com/BLSQ/openhexa-app/issues/1052)) ([7e462d4](https://github.com/BLSQ/openhexa-app/commit/7e462d487ad2dbc396e44f643dbae02b61522832))
* Redirect the url already hosted on Vercel to the new one in Django. ([#1058](https://github.com/BLSQ/openhexa-app/issues/1058)) ([fb61fc9](https://github.com/BLSQ/openhexa-app/commit/fb61fc91db2205cb6d537e9fcb96399f47222ca8))

## [1.3.0](https://github.com/BLSQ/openhexa-app/compare/1.2.4...1.3.0) (2025-04-24)


### Features

* **dataset:** add markdown editor to dataset (HEXA-1204)  ([#1032](https://github.com/BLSQ/openhexa-app/issues/1032)) ([93df72a](https://github.com/BLSQ/openhexa-app/commit/93df72aa68779a165f00b7c5185512b549da688e))
* **pipeline:** adds pipeline editor to pipeline and template (HEXA-1202) ([#1031](https://github.com/BLSQ/openhexa-app/issues/1031)) ([0d3ea9e](https://github.com/BLSQ/openhexa-app/commit/0d3ea9e788f8403f5377cca84a542a7286591ee4))


### Bug Fixes

* **deps:** update dependency @apollo/client to v3.13.8 ([#1041](https://github.com/BLSQ/openhexa-app/issues/1041)) ([5648259](https://github.com/BLSQ/openhexa-app/commit/5648259f9c67bddf29ba516e6295da8297071cf7))
* **deps:** update dependency @headlessui/react to v2.2.2 ([#1039](https://github.com/BLSQ/openhexa-app/issues/1039)) ([00e7091](https://github.com/BLSQ/openhexa-app/commit/00e7091ed2b7d6aed5f371bebbe0244cff02ef9f))
* **deps:** update dependency @mdxeditor/editor to v3.30.1 ([#1044](https://github.com/BLSQ/openhexa-app/issues/1044)) ([c266a67](https://github.com/BLSQ/openhexa-app/commit/c266a6759a6795e6ef485c45649dd8514273771c))
* **deps:** update dependency i18next to v25.0.1 ([#1048](https://github.com/BLSQ/openhexa-app/issues/1048)) ([421a93c](https://github.com/BLSQ/openhexa-app/commit/421a93cb9371a1e6086bb4d853ba5e27927adb4a))
* **deps:** update nextjs monorepo to v15.3.1 ([#1042](https://github.com/BLSQ/openhexa-app/issues/1042)) ([c9d0cf8](https://github.com/BLSQ/openhexa-app/commit/c9d0cf8351b5be9bbbccd68e9e071f93080c0d83))
* fixe pipeline parameter update in version picker ([#1053](https://github.com/BLSQ/openhexa-app/issues/1053)) ([eda92a5](https://github.com/BLSQ/openhexa-app/commit/eda92a50cf89852f9ce6919f059fcdece404b4bc))

## [1.2.4](https://github.com/BLSQ/openhexa-app/compare/1.2.3...1.2.4) (2025-04-17)


### Bug Fixes

* **deps:** update dependency @sentry/nextjs to v9.13.0 ([#1033](https://github.com/BLSQ/openhexa-app/issues/1033)) ([27f1a80](https://github.com/BLSQ/openhexa-app/commit/27f1a8077cb69b1f91a99a1a1114956cf4764da3))
* **deps:** update dependency i18next to v25 ([#1025](https://github.com/BLSQ/openhexa-app/issues/1025)) ([a69b603](https://github.com/BLSQ/openhexa-app/commit/a69b603c1f91d180f0bb0cdfd0cebe70145b18f7))
* **DHIS2:** organisation_unit_levels did not support filters parameter OPENHEXA-1H1 ([#1036](https://github.com/BLSQ/openhexa-app/issues/1036)) ([e078366](https://github.com/BLSQ/openhexa-app/commit/e078366e801d60616f537865b63e765114d3ed2e))
* **mixpanel:** serilize ids for tracking emails ([#1035](https://github.com/BLSQ/openhexa-app/issues/1035)) ([7ce9bbd](https://github.com/BLSQ/openhexa-app/commit/7ce9bbd18ef3f4362c12aeb176067d958804fadc))

## [1.2.3](https://github.com/BLSQ/openhexa-app/compare/1.2.2...1.2.3) (2025-04-14)


### Bug Fixes

* **deps:** update dependency @mdxeditor/editor to v3.30.0 ([#1018](https://github.com/BLSQ/openhexa-app/issues/1018)) ([f6b0244](https://github.com/BLSQ/openhexa-app/commit/f6b024464e7ecb1854ba7d729507ab185bdb4bd0))
* **deps:** update dependency @tanstack/react-table to v8.21.3 ([#1024](https://github.com/BLSQ/openhexa-app/issues/1024)) ([23ee56b](https://github.com/BLSQ/openhexa-app/commit/23ee56bfb9ef7eb039286a69fe5468eb93389c57))
* **deps:** update dependency @types/node to v22.14.1 ([#1016](https://github.com/BLSQ/openhexa-app/issues/1016)) ([664a87a](https://github.com/BLSQ/openhexa-app/commit/664a87afbc360c27b575dfd2cb4a67cea127646a))

## [1.2.2](https://github.com/BLSQ/openhexa-app/compare/1.2.1...1.2.2) (2025-04-11)


### Bug Fixes

* **deps:** update dependency @apollo/client to v3.13.7 ([#1011](https://github.com/BLSQ/openhexa-app/issues/1011)) ([e1abdcb](https://github.com/BLSQ/openhexa-app/commit/e1abdcb947d9e7d75183a311ee8f898d1915fc21))
* **deps:** update dependency dotenv to v16.5.0 ([#1012](https://github.com/BLSQ/openhexa-app/issues/1012)) ([3aa6f5f](https://github.com/BLSQ/openhexa-app/commit/3aa6f5f6c3ccde965e0fafb389573b24b109b68b))
* **deps:** update dependency react-hotkeys-hook to v5 ([#1005](https://github.com/BLSQ/openhexa-app/issues/1005)) ([79d773a](https://github.com/BLSQ/openhexa-app/commit/79d773a04eb2393cd283170340e2ef670946ba67))
* **deps:** update nextjs monorepo to v15.3.0 ([#1008](https://github.com/BLSQ/openhexa-app/issues/1008)) ([6dacb14](https://github.com/BLSQ/openhexa-app/commit/6dacb1438b91a1e606d12a2a9d080e48e2ae8080))
* fixes reference to datasets ([#1013](https://github.com/BLSQ/openhexa-app/issues/1013)) ([a1d8f27](https://github.com/BLSQ/openhexa-app/commit/a1d8f27b5d66b1d3a96ac76a10767308517d5edf))
* remove double slash on images url in the mails ([#1004](https://github.com/BLSQ/openhexa-app/issues/1004)) ([883c8b3](https://github.com/BLSQ/openhexa-app/commit/883c8b3906f8af964963b870259286d82312e93d))

## [1.2.1](https://github.com/BLSQ/openhexa-app/compare/1.2.0...1.2.1) (2025-04-09)


### Bug Fixes

* **deps:** update dependency @mdxeditor/editor to v3.29.3 ([#1001](https://github.com/BLSQ/openhexa-app/issues/1001)) ([75d7ba7](https://github.com/BLSQ/openhexa-app/commit/75d7ba7dd18175d1758686a5e9ab079993ccf45e))
* **deps:** update dependency react-hotkeys-hook to v4.6.2 ([#1002](https://github.com/BLSQ/openhexa-app/issues/1002)) ([b94570e](https://github.com/BLSQ/openhexa-app/commit/b94570ebab58cd0a5b3fafc5eba5c72e6c258928))

## [1.2.0](https://github.com/BLSQ/openhexa-app/compare/1.1.0...1.2.0) (2025-04-09)


### Features

* Improve web apps ([#965](https://github.com/BLSQ/openhexa-app/issues/965)) ([81792b2](https://github.com/BLSQ/openhexa-app/commit/81792b2411eb59d0cfd26acc3fdbd24661a29915))


### Bug Fixes

* **deps:** update dependency @sentry/nextjs to v9.12.0 ([#997](https://github.com/BLSQ/openhexa-app/issues/997)) ([70c2a18](https://github.com/BLSQ/openhexa-app/commit/70c2a18bdf7c8890d696c66aa330a9636b395690))
* **deps:** update dependency cronstrue to v2.59.0 ([#1000](https://github.com/BLSQ/openhexa-app/issues/1000)) ([4c796fd](https://github.com/BLSQ/openhexa-app/commit/4c796fd4059943a1c3b3bc6241d0aedd1637b1ae))
* **deps:** update nextjs monorepo to v15.2.5 ([#999](https://github.com/BLSQ/openhexa-app/issues/999)) ([90c8bdb](https://github.com/BLSQ/openhexa-app/commit/90c8bdb23da50617be0e7f2ccc7d8f43723b0fa1))
* docker-compose ([#994](https://github.com/BLSQ/openhexa-app/issues/994)) ([8e9401e](https://github.com/BLSQ/openhexa-app/commit/8e9401e569e8fc35d95148fa5e7b6264c4467281))
* readme env handling ([#995](https://github.com/BLSQ/openhexa-app/issues/995)) ([ab2a0ff](https://github.com/BLSQ/openhexa-app/commit/ab2a0ff21dd2e6fa38f1f3770065dbc06410b51e))

## [1.1.0](https://github.com/BLSQ/openhexa-app/compare/1.0.2...1.1.0) (2025-04-08)


### Features

* add email tracking to mixpanel ([#972](https://github.com/BLSQ/openhexa-app/issues/972)) ([7fe09c5](https://github.com/BLSQ/openhexa-app/commit/7fe09c52911be4d78f874263650d61c1272b140c))


### Bug Fixes

* align markdown configuration with live demo of MDXEditor ([4331b12](https://github.com/BLSQ/openhexa-app/commit/4331b1278ea78ac4c18812721d8d072e35c7d651))
* **deps:** update dependency @apollo/client to v3.13.6 ([#978](https://github.com/BLSQ/openhexa-app/issues/978)) ([7bc666b](https://github.com/BLSQ/openhexa-app/commit/7bc666ba300e6d9679e313484faecc9697fa9cac))
* **deps:** update dependency @headlessui/react to v2.2.1 ([#979](https://github.com/BLSQ/openhexa-app/issues/979)) ([606c360](https://github.com/BLSQ/openhexa-app/commit/606c3603077f5cd9befc19100ac164f7b5ff295a))
* **deps:** update dependency @mdxeditor/editor to v3.29.2 ([#980](https://github.com/BLSQ/openhexa-app/issues/980)) ([75eb183](https://github.com/BLSQ/openhexa-app/commit/75eb18311b373f073ff82dd643c17077e47d197e))
* **deps:** update dependency @sentry/nextjs to v9.11.0 ([#983](https://github.com/BLSQ/openhexa-app/issues/983)) ([a2c6afb](https://github.com/BLSQ/openhexa-app/commit/a2c6afb637752bdb13c9d8442bfe749287dca6d6))
* **deps:** update dependency @types/node to v22.14.0 ([#984](https://github.com/BLSQ/openhexa-app/issues/984)) ([3663086](https://github.com/BLSQ/openhexa-app/commit/36630863f4c1c0101789ee60464fe0c408b64a02))
* **deps:** update dependency cron-parser to v5 ([#987](https://github.com/BLSQ/openhexa-app/issues/987)) ([00b4c30](https://github.com/BLSQ/openhexa-app/commit/00b4c30d8d0cace6aac7bb1447f053e601d4d80a))
* **deps:** update dependency cronstrue to v2.58.0 ([#985](https://github.com/BLSQ/openhexa-app/issues/985)) ([474204a](https://github.com/BLSQ/openhexa-app/commit/474204a876e15fb7268e60e911ef9c69f221587f))
* **deps:** update dependency typescript to v5.8.3 ([#981](https://github.com/BLSQ/openhexa-app/issues/981)) ([9ac2b01](https://github.com/BLSQ/openhexa-app/commit/9ac2b01463f4bcd5a247ddcf5ea339f5bb8ad9a5))
* **deps:** update react monorepo to v19 ([#988](https://github.com/BLSQ/openhexa-app/issues/988)) ([30a618e](https://github.com/BLSQ/openhexa-app/commit/30a618ebc3cafced1e20bbfe913d31f1ea2cf28f))
* react update + Fix docker-compose ([#991](https://github.com/BLSQ/openhexa-app/issues/991)) ([4f0ea46](https://github.com/BLSQ/openhexa-app/commit/4f0ea4634dae5ead37145fbbc485c5c321329a48))

## [1.0.2](https://github.com/BLSQ/openhexa-app/compare/1.0.1...1.0.2) (2025-04-03)


### Bug Fixes

* **release-please:** Version the root & set version in components using extra-files ([4ce9a04](https://github.com/BLSQ/openhexa-app/commit/4ce9a0404e16fc71a1ff5cd3fe083ba06d042615))
* Set component name for the packages + version all components at once ([f98a089](https://github.com/BLSQ/openhexa-app/commit/f98a089720ac6bb503acc97c1fe2781ca5f8e403))


### Miscellaneous Chores

* Release 1.0.2 ([4d6db41](https://github.com/BLSQ/openhexa-app/commit/4d6db4174e18d3cd296b58f20510daf3a9ccc227))

## Changelog

## Backend

For detailed changes in the backend, please refer to the [Backend Changelog](backend/CHANGELOG.md).

## Frontend

For detailed changes in the frontend, please refer to the [Frontend Changelog](frontend/CHANGELOG.md).
