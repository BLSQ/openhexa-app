# Changelog

## [0.47.0](https://github.com/BLSQ/openhexa-frontend/compare/0.46.0...0.47.0) (2024-04-15)


### Features

* Users can update their pipelines' versions ([#594](https://github.com/BLSQ/openhexa-frontend/issues/594)) ([147dcf7](https://github.com/BLSQ/openhexa-frontend/commit/147dcf7019c4382f33fc15450ca8ba2072c4f891))


### Bug Fixes

* **Sentry:** Bundle size is enormous with Sentry. Let's try to reduce it ([#593](https://github.com/BLSQ/openhexa-frontend/issues/593)) ([9d9ff77](https://github.com/BLSQ/openhexa-frontend/commit/9d9ff77a88c215769fd1e26ee34a2fbea07ccbf9))


### Miscellaneous

* **CI:** Cache docker images in the registry (bigger cache than on GHA) ([e520c52](https://github.com/BLSQ/openhexa-frontend/commit/e520c527c87778ca17580f45379d6620a9ef06c9))
* **debt:** Remove catalog, search and revamp the menu of the user ([#592](https://github.com/BLSQ/openhexa-frontend/issues/592)) ([5b04fc0](https://github.com/BLSQ/openhexa-frontend/commit/5b04fc00fc85b6a0fd15eb55097b18d749e736a6))
* Uncomment dependencies caching task ([02d0838](https://github.com/BLSQ/openhexa-frontend/commit/02d083839a6b1adcc4211b3027fee56e0c0dafac))

## [0.46.0](https://github.com/BLSQ/openhexa-frontend/compare/0.45.2...0.46.0) (2024-04-05)


### Features

* **Pipelines:** Add version's name, description & link to the web UI ([#585](https://github.com/BLSQ/openhexa-frontend/issues/585)) ([38022c0](https://github.com/BLSQ/openhexa-frontend/commit/38022c0fe758c0a04c6752997cd0809596919dab))
* **Pipelines:** allow user to delete pipeline ([#569](https://github.com/BLSQ/openhexa-frontend/issues/569)) ([1c55dfb](https://github.com/BLSQ/openhexa-frontend/commit/1c55dfb950eef3e1d7d534686c2d3a203294c23b))
* **Pipelines:** allow user to stop a running/queued pipeline ([#587](https://github.com/BLSQ/openhexa-frontend/issues/587)) ([a62786c](https://github.com/BLSQ/openhexa-frontend/commit/a62786c1a32c5a4bd44d9f607f9053c2a35a9ccc))


### Miscellaneous

* Add swc to package-lock.json ([fd41a99](https://github.com/BLSQ/openhexa-frontend/commit/fd41a99ba693210cd736f68d3216fc75b82f28f9))
* **deps:** Update all js dependencies ([#586](https://github.com/BLSQ/openhexa-frontend/issues/586)) ([bf4c280](https://github.com/BLSQ/openhexa-frontend/commit/bf4c28001afeaf249850270a56729baa23751b3f))

## [0.45.2](https://github.com/BLSQ/openhexa-frontend/compare/0.45.1...0.45.2) (2024-02-26)


### Miscellaneous

* **Build:** Analyze the chunks and minimize what is served to the client ([#570](https://github.com/BLSQ/openhexa-frontend/issues/570)) ([0c16669](https://github.com/BLSQ/openhexa-frontend/commit/0c16669733f4615f5a65c0154cfa5a3c833d1511))
* **deps:** Update next & relatives to latest version ([#565](https://github.com/BLSQ/openhexa-frontend/issues/565)) ([ed993a0](https://github.com/BLSQ/openhexa-frontend/commit/ed993a0cdb1ca6ba50bcaef67939258fce926a31))
* **Telemetry:** Telemetry can be enabled with the env variable 'TELEMETRY_ID' ([#572](https://github.com/BLSQ/openhexa-frontend/issues/572)) ([7fd7c9a](https://github.com/BLSQ/openhexa-frontend/commit/7fd7c9a8718f65c541be8650c82e2c8327d30151))

## [0.45.1](https://github.com/BLSQ/openhexa-frontend/compare/0.45.0...0.45.1) (2024-02-20)


### Bug Fixes

* **Sidebar:** In compact mode, the sidebar labels were under the tables ([#562](https://github.com/BLSQ/openhexa-frontend/issues/562)) ([3d11ce7](https://github.com/BLSQ/openhexa-frontend/commit/3d11ce77c68a4d99511f8ae3a314e3f95dd18224))


### Miscellaneous

* **docker:** Improve caching ([6baae8b](https://github.com/BLSQ/openhexa-frontend/commit/6baae8b55830355784d0d83b9741696503b337e7))

## [0.45.0](https://github.com/BLSQ/openhexa-frontend/compare/0.44.1...0.45.0) (2024-02-19)


### Features

* Download pipeline versions ([#561](https://github.com/BLSQ/openhexa-frontend/issues/561)) ([cf335da](https://github.com/BLSQ/openhexa-frontend/commit/cf335dad49690f252f3379ffa7c4f84e2432345e))


### Bug Fixes

* **Datasets:** Fix the example snippet on how to use the sdk to create a version ([af35fbe](https://github.com/BLSQ/openhexa-frontend/commit/af35fbe239f40f5ffdd1fd5f559c16336e02faf6))
* **Files:** Search for files works on FF & Chrome ([#560](https://github.com/BLSQ/openhexa-frontend/issues/560)) ([ccc97b7](https://github.com/BLSQ/openhexa-frontend/commit/ccc97b7c72f16ebbf06dcdc5ef0bf3db939a8c22))
* **Login:** fix error spacing; Add an alert when user asks for a new code ([#564](https://github.com/BLSQ/openhexa-frontend/issues/564)) ([5e40ac3](https://github.com/BLSQ/openhexa-frontend/commit/5e40ac3d712ef06474481a22be0d6306c93e7e56))
* **PipelineRun:** include dataset versions output to runOuputs ([#557](https://github.com/BLSQ/openhexa-frontend/issues/557)) ([b3a42c9](https://github.com/BLSQ/openhexa-frontend/commit/b3a42c9293b417d3a160082cdbda05268284a668))


### Miscellaneous

* Add the compat for next types ([ae7d191](https://github.com/BLSQ/openhexa-frontend/commit/ae7d191f82d3f7c95a38160846f63a042416c860))

## [0.44.1](https://github.com/BLSQ/openhexa-frontend/compare/0.44.0...0.44.1) (2024-02-07)


### Miscellaneous

* Minor changes on dockerfile ([15aaf49](https://github.com/BLSQ/openhexa-frontend/commit/15aaf492176b5bd5ae2b1ab345252b131ac94851))
* update dockerfile to use node 20 ([#552](https://github.com/BLSQ/openhexa-frontend/issues/552)) ([8cf7d71](https://github.com/BLSQ/openhexa-frontend/commit/8cf7d7115f212c4fb8a7cc5bf0f2f7f0b0f1ce77))

## [0.44.0](https://github.com/BLSQ/openhexa-frontend/compare/0.43.1...0.44.0) (2024-02-06)


### Features

* **Pipeline:** add support for dataset parameter ([#545](https://github.com/BLSQ/openhexa-frontend/issues/545)) ([cd8d024](https://github.com/BLSQ/openhexa-frontend/commit/cd8d024869a5e61c4c9964654203a9379fcebff3))


### Bug Fixes

* **Schema:** Add a BigInt scalar ([#553](https://github.com/BLSQ/openhexa-frontend/issues/553)) ([524ba2a](https://github.com/BLSQ/openhexa-frontend/commit/524ba2a6b9c78d13bf39b18ce0b35f803c436e06))

## [0.43.1](https://github.com/BLSQ/openhexa-frontend/compare/0.43.0...0.43.1) (2024-02-05)


### Bug Fixes

* **Files:** hide upload and create button for viewer ([#546](https://github.com/BLSQ/openhexa-frontend/issues/546)) ([f56b352](https://github.com/BLSQ/openhexa-frontend/commit/f56b352a10c3a666ac86eb50c39bd8dfe50b670c))

## [0.43.0](https://github.com/BLSQ/openhexa-frontend/compare/0.42.5...0.43.0) (2024-01-30)


### Features

* **PipelineRun:** display run dataset versions ([#536](https://github.com/BLSQ/openhexa-frontend/issues/536)) ([a25680b](https://github.com/BLSQ/openhexa-frontend/commit/a25680b9e62713bdc2e7c4c61f03242ab1221884))
* **Pipelines:** Show the parameters & versions on the page ([#539](https://github.com/BLSQ/openhexa-frontend/issues/539)) ([d38c0f5](https://github.com/BLSQ/openhexa-frontend/commit/d38c0f5d4347093f81d6569ca733e6570546a5dc))


### Bug Fixes

* **Files:** search was not working on Chrome (weird bug on thie browser) ([#544](https://github.com/BLSQ/openhexa-frontend/issues/544)) ([c93fa64](https://github.com/BLSQ/openhexa-frontend/commit/c93fa64098da9afba4734e59cb3ebc59170c4c7a))
* **Pipelines:** null & empty values for int and float should be ignored ([#540](https://github.com/BLSQ/openhexa-frontend/issues/540)) ([2b2d4a8](https://github.com/BLSQ/openhexa-frontend/commit/2b2d4a82e4a02bbe4cff56950c167ad84e9eb04e))
* **Pipelines:** Only display the 'run again' button for finished runs ([#541](https://github.com/BLSQ/openhexa-frontend/issues/541)) ([a56438e](https://github.com/BLSQ/openhexa-frontend/commit/a56438e7619124f4aa9589d3dc96032d3b24ec79))
* **Sidebar:** Home was not selected in the sidebar when on the page ([852cd08](https://github.com/BLSQ/openhexa-frontend/commit/852cd086a675383c7319af69357645090fc89e74))

## [0.42.5](https://github.com/BLSQ/openhexa-frontend/compare/0.42.4...0.42.5) (2024-01-24)


### Bug Fixes

* **i18n:** Adapt translations ([0820ae6](https://github.com/BLSQ/openhexa-frontend/commit/0820ae6b0dee3d207d2276c61eb774caa205c143))
* **i18n:** Fix variable placeholders in french ([32f4951](https://github.com/BLSQ/openhexa-frontend/commit/32f495114e349903bb14973b1e2088b5527f5172))
* **i18n:** Fix wrong translation ([ff7441f](https://github.com/BLSQ/openhexa-frontend/commit/ff7441f25bdb7abfb40b55dda34b870b1429a5b8))
* **i18n:** improve translations ([ee46e90](https://github.com/BLSQ/openhexa-frontend/commit/ee46e9056e0dd475ba9ceca1aa387147d19d6508))


### Miscellaneous

* **i18n:** improve messages ([d9398e8](https://github.com/BLSQ/openhexa-frontend/commit/d9398e8de029733c2233202587166350b7ae4e7e))
* **i18n:** update messages ([db4d64a](https://github.com/BLSQ/openhexa-frontend/commit/db4d64af47ac7a161f76bd68484f624213b9fa71))

## [0.42.4](https://github.com/BLSQ/openhexa-frontend/compare/0.42.3...0.42.4) (2024-01-17)


### Miscellaneous

* **i18n:** update fr messages ([1b923bd](https://github.com/BLSQ/openhexa-frontend/commit/1b923bd614c1dcae71ff45a97b7098bedd2941e7))

## [0.42.3](https://github.com/BLSQ/openhexa-frontend/compare/0.42.2...0.42.3) (2024-01-11)


### Miscellaneous

* **i18n:** update messages ([b084beb](https://github.com/BLSQ/openhexa-frontend/commit/b084bebe1fc72a1b9a8f6152b66fa6dd7405611c))
* **i18n:** Validate that all strings are translated ([#531](https://github.com/BLSQ/openhexa-frontend/issues/531)) ([f84e5bd](https://github.com/BLSQ/openhexa-frontend/commit/f84e5bd4e3ec2c25db695bbe354437dd41615c7b))

## [0.42.2](https://github.com/BLSQ/openhexa-frontend/compare/0.42.1...0.42.2) (2024-01-11)


### Bug Fixes

* **files:** Replace the default value of query by an empty string ([#527](https://github.com/BLSQ/openhexa-frontend/issues/527)) ([696821e](https://github.com/BLSQ/openhexa-frontend/commit/696821ea04b4b91be053244dbf43ee902d4b1a56))
* **Invitations:** Improve the display of the invitations on the account page ([#526](https://github.com/BLSQ/openhexa-frontend/issues/526)) ([059313f](https://github.com/BLSQ/openhexa-frontend/commit/059313f4feb5c6061cd536c1d36c4d6cea0413ac))


### Miscellaneous

* **i18n:** Add a script to translate messages using Deep ([#528](https://github.com/BLSQ/openhexa-frontend/issues/528)) ([448ea5b](https://github.com/BLSQ/openhexa-frontend/commit/448ea5be81359998099b288a47e8a048093689a0))

## [0.42.1](https://github.com/BLSQ/openhexa-frontend/compare/0.42.0...0.42.1) (2024-01-08)


### Bug Fixes

* **i18n:** Fix placeholders ([7a4aaf9](https://github.com/BLSQ/openhexa-frontend/commit/7a4aaf947fd2076d2ba7fbf46b0a40a69cd7b180))
* Missing fr translations ([914d4fc](https://github.com/BLSQ/openhexa-frontend/commit/914d4fc50e5ad4fe15a4f4e6dccd690c9cb54070))

## [0.42.0](https://github.com/BLSQ/openhexa-frontend/compare/0.41.3...0.42.0) (2024-01-08)


### Features

* **Files:** Size options & Objects filtering ([#516](https://github.com/BLSQ/openhexa-frontend/issues/516)) ([ea89afe](https://github.com/BLSQ/openhexa-frontend/commit/ea89afefa8636ad6e35d2778e737e82f74ae8669))
* **i18n:** Translate web app in French ([#518](https://github.com/BLSQ/openhexa-frontend/issues/518)) ([f70e1ef](https://github.com/BLSQ/openhexa-frontend/commit/f70e1ef3fe8b538a3692bb67c96941b2812d9049))
* Register page & Decline invitations ([#513](https://github.com/BLSQ/openhexa-frontend/issues/513)) ([8e8ef5d](https://github.com/BLSQ/openhexa-frontend/commit/8e8ef5d3b37f7a797ef9cb77ec027a55594fb677))

## [0.41.3](https://github.com/BLSQ/openhexa-frontend/compare/0.41.2...0.41.3) (2023-12-29)


### Bug Fixes

* use POST request for logout ([#514](https://github.com/BLSQ/openhexa-frontend/issues/514)) ([71eb61f](https://github.com/BLSQ/openhexa-frontend/commit/71eb61f2e36b172ff522645f91c3c82c4ec9e5a8))

## [0.41.2](https://github.com/BLSQ/openhexa-frontend/compare/0.41.1...0.41.2) (2023-12-26)


### Bug Fixes

* Improve run messages ([#510](https://github.com/BLSQ/openhexa-frontend/issues/510)) ([1998ff9](https://github.com/BLSQ/openhexa-frontend/commit/1998ff956c6dd1c272e007a0ce5478c480c85930))
* **Pipelines:** Add a 'Webhook' run trigger & Improve parameters display ([#509](https://github.com/BLSQ/openhexa-frontend/issues/509)) ([fc090e6](https://github.com/BLSQ/openhexa-frontend/commit/fc090e664c8d1b3ec870dfdd72881cdd04792086))

## [0.41.1](https://github.com/BLSQ/openhexa-frontend/compare/0.41.0...0.41.1) (2023-12-19)


### Bug Fixes

* **Pipelines:** Use the feature flag to hide/show the webhook section ([ced62f3](https://github.com/BLSQ/openhexa-frontend/commit/ced62f3cca308bbc90434530054bb871a1500956))

## [0.41.0](https://github.com/BLSQ/openhexa-frontend/compare/0.40.0...0.41.0) (2023-12-19)


### Features

* **Pipelines:** Add a webhook mechanism on the pipelines ([#507](https://github.com/BLSQ/openhexa-frontend/issues/507)) ([6b0a53a](https://github.com/BLSQ/openhexa-frontend/commit/6b0a53a210f1e08168974701cde08870f22cb8ea))


### Miscellaneous

* disable search for now ([#503](https://github.com/BLSQ/openhexa-frontend/issues/503)) ([723d646](https://github.com/BLSQ/openhexa-frontend/commit/723d64645c2caad8d717746c9b66f38919b75d57))

## [0.40.0](https://github.com/BLSQ/openhexa-frontend/compare/0.39.0...0.40.0) (2023-12-14)


### Features

* **PipelineRun:** Improve messages list ([#502](https://github.com/BLSQ/openhexa-frontend/issues/502)) ([b13fef0](https://github.com/BLSQ/openhexa-frontend/commit/b13fef0bbcca3e6bc694a45476a3f35151e5da93))


### Bug Fixes

* **Overflow:** Fix overflow in vertical mode ([#501](https://github.com/BLSQ/openhexa-frontend/issues/501)) ([20ad684](https://github.com/BLSQ/openhexa-frontend/commit/20ad68403084cc33cb57569104dfed2479852388))
* **Workspace:** Remove TOKEN_EXPIRED & Handle the need to authenticate in the join workspace workflow ([#499](https://github.com/BLSQ/openhexa-frontend/issues/499)) ([1ba5859](https://github.com/BLSQ/openhexa-frontend/commit/1ba585952db76a7d5eacf448a4d6b64777bd4b41))


### Miscellaneous

* **deps:** bump @graphql-codegen/typescript-react-apollo from 4.0.0 to 4.1.0 ([#486](https://github.com/BLSQ/openhexa-frontend/issues/486)) ([f27342f](https://github.com/BLSQ/openhexa-frontend/commit/f27342f4ab2ae5d312747a3ed0f8988a96b0a514))
* **deps:** bump @uiw/react-codemirror from 4.21.13 to 4.21.21 ([#487](https://github.com/BLSQ/openhexa-frontend/issues/487)) ([7151c0a](https://github.com/BLSQ/openhexa-frontend/commit/7151c0aff819e6f7176afe460e5b4f4ba90ad5de))

## [0.39.0](https://github.com/BLSQ/openhexa-frontend/compare/0.38.0...0.39.0) (2023-12-06)


### Features

* **PipelineRun:** use linkify-react for url parsing ([#497](https://github.com/BLSQ/openhexa-frontend/issues/497)) ([7f1699a](https://github.com/BLSQ/openhexa-frontend/commit/7f1699a0f70e5bcbf05dd6fefc18ee203c845db8))
* **Workspaces:** increase workspace members page size to 10 ([#496](https://github.com/BLSQ/openhexa-frontend/issues/496)) ([bc541f9](https://github.com/BLSQ/openhexa-frontend/commit/bc541f94435fac87d5c02c27e055a726b67b960a))

## [0.38.0](https://github.com/BLSQ/openhexa-frontend/compare/0.37.0...0.38.0) (2023-12-04)


### Features

* **Pipelines:** improve pipeline messages UX ([#489](https://github.com/BLSQ/openhexa-frontend/issues/489)) ([e75c929](https://github.com/BLSQ/openhexa-frontend/commit/e75c929926080e24654e624fa6fee90f8cc51333))


### Bug Fixes

* add missing 'remark-gfm' package ([01c79f4](https://github.com/BLSQ/openhexa-frontend/commit/01c79f4258d90f96a512f2343437577a65578f33))
* **ConnectionPicker:** use id for connection identifier ([#493](https://github.com/BLSQ/openhexa-frontend/issues/493)) ([841e08b](https://github.com/BLSQ/openhexa-frontend/commit/841e08b1ec4ba224ce66d8f079292347a60e9d9e))


### Miscellaneous

* clean up ([#495](https://github.com/BLSQ/openhexa-frontend/issues/495)) ([2e1f57d](https://github.com/BLSQ/openhexa-frontend/commit/2e1f57d7653d298bf3103e447fbc3ea3d4cb91c0))
* Delete vite.config.ts ([8efd278](https://github.com/BLSQ/openhexa-frontend/commit/8efd278a7c72840abbf487ec90b4e94e23b89b03))
* **Nextjs:** Add a trailing slash to nextjs urls ([af709b2](https://github.com/BLSQ/openhexa-frontend/commit/af709b28e2474681463f08a8b9c2642759f55521))
* remove ladle ([#491](https://github.com/BLSQ/openhexa-frontend/issues/491)) ([16b3081](https://github.com/BLSQ/openhexa-frontend/commit/16b30818bf646d28f36866b1712e55efb237adac))

## [0.37.0](https://github.com/BLSQ/openhexa-frontend/compare/0.36.10...0.37.0) (2023-11-24)


### Features

* **Pipelines:** add CTA when pipeline screen is empty ([#484](https://github.com/BLSQ/openhexa-frontend/issues/484)) ([7688f8e](https://github.com/BLSQ/openhexa-frontend/commit/7688f8e57455e01bcac983eb18017bf9f8e97580))


### Bug Fixes

* **Connections:** hide s3 connection secret key ([#482](https://github.com/BLSQ/openhexa-frontend/issues/482)) ([38b9924](https://github.com/BLSQ/openhexa-frontend/commit/38b99246ae6d06467a6bd52cbc01bdca706a50d3))
* **PipelineDialog:** prevent display of empty value on picker ([#481](https://github.com/BLSQ/openhexa-frontend/issues/481)) ([435118b](https://github.com/BLSQ/openhexa-frontend/commit/435118b6b8059a95b56004a5096c8ba60e6ffec7))


### Miscellaneous

* release please bump policy change ([#485](https://github.com/BLSQ/openhexa-frontend/issues/485)) ([e9151c1](https://github.com/BLSQ/openhexa-frontend/commit/e9151c18f650947573e39580f3889989e6ca65e0))

## [0.36.10](https://github.com/BLSQ/openhexa-frontend/compare/0.36.9...0.36.10) (2023-11-18)


### Features

* **Pipelines:** Add connection picker ([#476](https://github.com/BLSQ/openhexa-frontend/issues/476)) ([98dd463](https://github.com/BLSQ/openhexa-frontend/commit/98dd4631e863678115d9e2a6617855ef4c75bfac))

## [0.36.9](https://github.com/BLSQ/openhexa-frontend/compare/0.36.8...0.36.9) (2023-11-14)


### Features

* add more info about regenerating workspace database passwords ([#474](https://github.com/BLSQ/openhexa-frontend/issues/474)) ([a9a133c](https://github.com/BLSQ/openhexa-frontend/commit/a9a133cbec1ffc2470c52f23b5805424a5d3598b))

## [0.36.8](https://github.com/BLSQ/openhexa-frontend/compare/0.36.7...0.36.8) (2023-11-10)


### Miscellaneous

* remove visualizations module ([#466](https://github.com/BLSQ/openhexa-frontend/issues/466)) ([c4c3204](https://github.com/BLSQ/openhexa-frontend/commit/c4c3204a3a937e8a3827b6fc8496bc764609d57e))

## [0.36.7](https://github.com/BLSQ/openhexa-frontend/compare/0.36.6...0.36.7) (2023-10-26)


### Bug Fixes

* **Pipelines:** Fix issues on multiple choice param ([#461](https://github.com/BLSQ/openhexa-frontend/issues/461)) ([b82e087](https://github.com/BLSQ/openhexa-frontend/commit/b82e087fc9bc15a325a9b795076092411dc9cc8e))
* **Pipelines:** Fix multiple float parameters display ([#464](https://github.com/BLSQ/openhexa-frontend/issues/464)) ([896b616](https://github.com/BLSQ/openhexa-frontend/commit/896b616f3923baa19f8897faf3519e81fb96f217))

## [0.36.6](https://github.com/BLSQ/openhexa-frontend/compare/0.36.5...0.36.6) (2023-10-18)


### Features

* **Datasets:** add help links ([#455](https://github.com/BLSQ/openhexa-frontend/issues/455)) ([8e386e9](https://github.com/BLSQ/openhexa-frontend/commit/8e386e9d9b662c1ed7467034a8f5bdc825c67b0b))
* **Pipelines:** Support multiple ints in pipeline ([#432](https://github.com/BLSQ/openhexa-frontend/issues/432)) ([55f9dce](https://github.com/BLSQ/openhexa-frontend/commit/55f9dce46c8ab439f8695e202d477fdad191cc8e))


### Bug Fixes

* **PipelineRun:** use PipelineRun timeout ([#452](https://github.com/BLSQ/openhexa-frontend/issues/452)) ([beb1553](https://github.com/BLSQ/openhexa-frontend/commit/beb1553e235e98b1997d7d66d83b5f36d315ef0f))


### Miscellaneous

* **deps:** bump next from 13.4.4 to 13.5.5 ([#458](https://github.com/BLSQ/openhexa-frontend/issues/458)) ([67fb065](https://github.com/BLSQ/openhexa-frontend/commit/67fb065792cd72b8ac5082c5d5e2bc8043341798))

## [0.36.5](https://github.com/BLSQ/openhexa-frontend/compare/0.36.4...0.36.5) (2023-10-11)


### Bug Fixes

* **Datasets:** Set create button on upload section ([#450](https://github.com/BLSQ/openhexa-frontend/issues/450)) ([f440080](https://github.com/BLSQ/openhexa-frontend/commit/f440080bb7b414d8fb707671e8c0cd08df00a2b7))

## [0.36.4](https://github.com/BLSQ/openhexa-frontend/compare/0.36.3...0.36.4) (2023-10-10)


### Bug Fixes

* **Datasets:** rename upload a version to create a version ([#448](https://github.com/BLSQ/openhexa-frontend/issues/448)) ([cf1a00a](https://github.com/BLSQ/openhexa-frontend/commit/cf1a00a532cc21f911bc6feeaac3b33443e72e75))

## [0.36.3](https://github.com/BLSQ/openhexa-frontend/compare/0.36.2...0.36.3) (2023-10-10)


### Bug Fixes

* **Connections:** rename IASO instance api_url to url ([#445](https://github.com/BLSQ/openhexa-frontend/issues/445)) ([1b41dd7](https://github.com/BLSQ/openhexa-frontend/commit/1b41dd74eb46bac9f3dc0e8c63ec107d240fcaee))
* **Datasets:** Update CTA to create a version; Update snippet ([#437](https://github.com/BLSQ/openhexa-frontend/issues/437)) ([66698af](https://github.com/BLSQ/openhexa-frontend/commit/66698afe4b8a126fece8ff89731e6f8a9589b010))

## [0.36.2](https://github.com/BLSQ/openhexa-frontend/compare/0.36.1...0.36.2) (2023-09-25)


### Bug Fixes

* Align vertically the label in description list ([#434](https://github.com/BLSQ/openhexa-frontend/issues/434)) ([037488f](https://github.com/BLSQ/openhexa-frontend/commit/037488f3a95e356b6d60e1e1eb24c4f1bc4856f1))
* **datasets:** add an ellipsis on the first column of the datasets list ([037488f](https://github.com/BLSQ/openhexa-frontend/commit/037488f3a95e356b6d60e1e1eb24c4f1bc4856f1))


### Miscellaneous

* **deps:** bump @uiw/react-codemirror from 4.20.2 to 4.21.13 ([#431](https://github.com/BLSQ/openhexa-frontend/issues/431)) ([65b85c7](https://github.com/BLSQ/openhexa-frontend/commit/65b85c7e9c5b67df2607fafe83b59e8120fa313c))

## [0.36.1](https://github.com/BLSQ/openhexa-frontend/compare/0.36.0...0.36.1) (2023-09-13)


### Features

* **Connections:** hide gcs connection service_account_key value ([#428](https://github.com/BLSQ/openhexa-frontend/issues/428)) ([373c73e](https://github.com/BLSQ/openhexa-frontend/commit/373c73e8bc8ca08657caf16d0d2f7a82ebadb505))


### Bug Fixes

* Align vertically the label in description list ([#427](https://github.com/BLSQ/openhexa-frontend/issues/427)) ([8b4d954](https://github.com/BLSQ/openhexa-frontend/commit/8b4d954b4ff131e567bc7a406dc5db32c51fb3b1))

## [0.36.0](https://github.com/BLSQ/openhexa-frontend/compare/0.35.1...0.36.0) (2023-09-12)


### Miscellaneous

* **Releases:** Prepare next release ([03745b6](https://github.com/BLSQ/openhexa-frontend/commit/03745b6494a4c7c22367b16980e3f9c443e86691))

## [0.35.1](https://github.com/BLSQ/openhexa-frontend/compare/0.35.0...0.35.1) (2023-09-12)


### Bug Fixes

* **Connections:** revert changes on doc links ([#424](https://github.com/BLSQ/openhexa-frontend/issues/424)) ([8ec73f8](https://github.com/BLSQ/openhexa-frontend/commit/8ec73f8036afd341293587b6dc2b915079ce57fb))

## [0.35.0](https://github.com/BLSQ/openhexa-frontend/compare/0.34.0...0.35.0) (2023-09-12)


### Features

* **Pipelines:** display timeout on pipeline run page ([#418](https://github.com/BLSQ/openhexa-frontend/issues/418)) ([975499e](https://github.com/BLSQ/openhexa-frontend/commit/975499e7bc274d422d411b503aae6d2e6607e0e1))


### Bug Fixes

* **Dialog:** Make the dialog's content scrollable ([#419](https://github.com/BLSQ/openhexa-frontend/issues/419)) ([9774720](https://github.com/BLSQ/openhexa-frontend/commit/9774720d2262ee41a3116a78361707df75e44498))
* Make the account page accessible to non legacy users ([18fe53f](https://github.com/BLSQ/openhexa-frontend/commit/18fe53f0bd9cab79844a277d8429450b21e97b9e))
* **Pipelines:** fix broken link in breadcrumbs ([#417](https://github.com/BLSQ/openhexa-frontend/issues/417)) ([d1512e4](https://github.com/BLSQ/openhexa-frontend/commit/d1512e4150a1e5c2ccbcd5e39ec2125ac9be2e6a))


### Miscellaneous

* **deps:** bump cron-parser from 4.8.1 to 4.9.0 ([#413](https://github.com/BLSQ/openhexa-frontend/issues/413)) ([5ca4310](https://github.com/BLSQ/openhexa-frontend/commit/5ca43103a4bbf9209cb7194c65b04f2acb2455f8))
* **deps:** bump jest-environment-jsdom from 29.4.1 to 29.6.4 ([#414](https://github.com/BLSQ/openhexa-frontend/issues/414)) ([5abc3c7](https://github.com/BLSQ/openhexa-frontend/commit/5abc3c7825a83127e8f9aad54ae36eba88390601))
* **Release:** Prepare release 0.35.0 ([56fdebc](https://github.com/BLSQ/openhexa-frontend/commit/56fdebc51d93f7d1ebad067abe265bc5c2299b9e))

## [0.34.0](https://github.com/BLSQ/openhexa-frontend/compare/0.33.6...0.34.0) (2023-08-21)


### Features

* **Overflow:** Add a overflow component that displays a gradient when there is an overflow ([5cae039](https://github.com/BLSQ/openhexa-frontend/commit/5cae03930f5e524be0a2c457e7b85bf9e35788ee))


### Miscellaneous

* Prepare release 0.34.0 ([d7387cc](https://github.com/BLSQ/openhexa-frontend/commit/d7387ccf1ba8478e5af0d7aeb333614a261b4034))

## [0.33.6](https://github.com/BLSQ/openhexa-frontend/compare/0.33.5...0.33.6) (2023-08-16)


### Bug Fixes

* **tests:** I broke the tests... ([c4ad3fb](https://github.com/BLSQ/openhexa-frontend/commit/c4ad3fb3eab5431d0507bd05e53b3cb3ed93b919))
* **WorkspaceLayout:** Fix problem with very tables with a lot of columns ([fb91722](https://github.com/BLSQ/openhexa-frontend/commit/fb91722b86ea4009ac6de6dca681083467d41ce7))

## [0.33.5](https://github.com/BLSQ/openhexa-frontend/compare/0.33.4...0.33.5) (2023-08-14)


### Bug Fixes

* **Layout:** Header was not sticky, make css simpler ([#407](https://github.com/BLSQ/openhexa-frontend/issues/407)) ([d66d96d](https://github.com/BLSQ/openhexa-frontend/commit/d66d96de4fcb13ade9ecde29b194debc35c0fc39))

## [0.33.4](https://github.com/BLSQ/openhexa-frontend/compare/0.33.3...0.33.4) (2023-08-14)


### Features

* **Pipelines:** Display nicely db & file outputs ([f77c51d](https://github.com/BLSQ/openhexa-frontend/commit/f77c51da9176f8a8c87c94e509718b203932b4a2))
* **Workspaces:** improve invitation management ([#400](https://github.com/BLSQ/openhexa-frontend/issues/400)) ([3536eff](https://github.com/BLSQ/openhexa-frontend/commit/3536effe34e53c7f85ad1fff4c6cfcfcb78a9945))


### Bug Fixes

* **Files:** Add a description on what does the toggle ([#401](https://github.com/BLSQ/openhexa-frontend/issues/401)) ([9663645](https://github.com/BLSQ/openhexa-frontend/commit/9663645726db5de61f16b16047e0bca84f44e9e6))
* **Workspace:** Layout is broken; Sidebar should not scroll ([#403](https://github.com/BLSQ/openhexa-frontend/issues/403)) ([e09c5c6](https://github.com/BLSQ/openhexa-frontend/commit/e09c5c617ac41694754543cb674ac41c601c31c7))

## [0.33.3](https://github.com/BLSQ/openhexa-frontend/compare/0.33.2...0.33.3) (2023-08-08)


### Features

* **Files:** Show/hide hidden files & directories ([#395](https://github.com/BLSQ/openhexa-frontend/issues/395)) ([903ac4f](https://github.com/BLSQ/openhexa-frontend/commit/903ac4fdd2894c55f570cc2f434d9313d5956c0b))


### Bug Fixes

* **Connections:** Hide 'add connection' button for non-admins ([#398](https://github.com/BLSQ/openhexa-frontend/issues/398)) ([e758916](https://github.com/BLSQ/openhexa-frontend/commit/e758916d37a702abf94108afefd4d3d8ab79a7bb))

## [0.33.2](https://github.com/BLSQ/openhexa-frontend/compare/0.33.1...0.33.2) (2023-07-31)


### Bug Fixes

* **Connections:** Only display the submitError element if there is an error ([d0b290d](https://github.com/BLSQ/openhexa-frontend/commit/d0b290db3989c36aabb059bd68f5120cdc32260e))
* **Connections:** Wrong permission was checked to display the create a connection dialog ([#392](https://github.com/BLSQ/openhexa-frontend/issues/392)) ([fdc3834](https://github.com/BLSQ/openhexa-frontend/commit/fdc3834fa80549652f2db290132251d0894c6abf))

## [0.33.1](https://github.com/BLSQ/openhexa-frontend/compare/0.33.0...0.33.1) (2023-07-25)


### Features

* **Workspaces:** set demo content optional ([#388](https://github.com/BLSQ/openhexa-frontend/issues/388)) ([9f268b9](https://github.com/BLSQ/openhexa-frontend/commit/9f268b9ed74c4c0ddafb77dfd31cb6449b2c92d9))

## [0.33.0](https://github.com/BLSQ/openhexa-frontend/compare/0.32.6...0.33.0) (2023-07-19)


### Features

* **Database:** User can select/deselect the columns he wants to see ([#382](https://github.com/BLSQ/openhexa-frontend/issues/382)) ([974ec3b](https://github.com/BLSQ/openhexa-frontend/commit/974ec3b8ef2e04710b0aa8017b386e4483fbf113))


### Bug Fixes

* **Modals:** prevent glitch when closing modal ([#377](https://github.com/BLSQ/openhexa-frontend/issues/377)) ([5274ab1](https://github.com/BLSQ/openhexa-frontend/commit/5274ab175bca0f85174da4163705eff7843e7fa3))
* **Pipelines:** allow scheduling for only pipelines without parameters ([#381](https://github.com/BLSQ/openhexa-frontend/issues/381)) ([47dad85](https://github.com/BLSQ/openhexa-frontend/commit/47dad85d773f5949cdf214c630bb75aba98515f7))


### Miscellaneous

* 'feat' creates a patch version and not a minor version ([434703c](https://github.com/BLSQ/openhexa-frontend/commit/434703c62cccbf206cc49481a12347e50c7b8b2d))
* Connections UX improvements ([#373](https://github.com/BLSQ/openhexa-frontend/issues/373)) ([386c8cf](https://github.com/BLSQ/openhexa-frontend/commit/386c8cf2047739f7d378d3598c695c2929af907c))
* **Connections:** update IASO logo ([#380](https://github.com/BLSQ/openhexa-frontend/issues/380)) ([6f73ff2](https://github.com/BLSQ/openhexa-frontend/commit/6f73ff2a853a86f71ad99f1cad6305bccb303c42))
* **deps:** bump semver from 5.7.1 to 5.7.2 ([#374](https://github.com/BLSQ/openhexa-frontend/issues/374)) ([1a97f5b](https://github.com/BLSQ/openhexa-frontend/commit/1a97f5b8525e0076cfb92eeedcfbce8f7b6b5479))
* **deps:** bump tough-cookie from 4.1.2 to 4.1.3 ([#368](https://github.com/BLSQ/openhexa-frontend/issues/368)) ([4696462](https://github.com/BLSQ/openhexa-frontend/commit/46964627217ca6cafe036994e218a3923eefbc81))
* **i18n:** update translations ([386c8cf](https://github.com/BLSQ/openhexa-frontend/commit/386c8cf2047739f7d378d3598c695c2929af907c))
* **Pipelines:** scheduling section ux fine-tuning ([#383](https://github.com/BLSQ/openhexa-frontend/issues/383)) ([5e3754f](https://github.com/BLSQ/openhexa-frontend/commit/5e3754fb35a95bef957cef32ff919780bb88977d))

## [0.32.6](https://github.com/BLSQ/openhexa-frontend/compare/0.32.5...0.32.6) (2023-07-13)


### Miscellaneous

* Help popup everywhere ([#376](https://github.com/BLSQ/openhexa-frontend/issues/376)) ([f5cb22e](https://github.com/BLSQ/openhexa-frontend/commit/f5cb22eec0ee34ae49bd42ad7b211a68ecd19d6c))

## [0.32.5](https://github.com/BLSQ/openhexa-frontend/compare/0.32.4...0.32.5) (2023-07-12)


### Bug Fixes

* Remove collections ([#367](https://github.com/BLSQ/openhexa-frontend/issues/367)) ([b21bab3](https://github.com/BLSQ/openhexa-frontend/commit/b21bab3a8e2f3825764b61cc0bdab9af40f7f2f2))


### Miscellaneous

* Remove collections ([b21bab3](https://github.com/BLSQ/openhexa-frontend/commit/b21bab3a8e2f3825764b61cc0bdab9af40f7f2f2))

## [0.32.4](https://github.com/BLSQ/openhexa-frontend/compare/0.32.3...0.32.4) (2023-07-11)


### Bug Fixes

* **Pipelines:** display correct trigger mode ([#371](https://github.com/BLSQ/openhexa-frontend/issues/371)) ([2fd5448](https://github.com/BLSQ/openhexa-frontend/commit/2fd544858dae2b9ab7161842053a59f35773316d))


### Miscellaneous

* **Workspaces:** allow admin to invite external users ([#370](https://github.com/BLSQ/openhexa-frontend/issues/370)) ([476a854](https://github.com/BLSQ/openhexa-frontend/commit/476a8547bb813f2905be66b8e727bbda368b76d3))

## [0.32.3](https://github.com/BLSQ/openhexa-frontend/compare/0.32.2...0.32.3) (2023-07-04)


### Bug Fixes

* Uncomment runs block on the pipeline page ([#365](https://github.com/BLSQ/openhexa-frontend/issues/365)) ([0cc7a00](https://github.com/BLSQ/openhexa-frontend/commit/0cc7a0029582174df4a85bb9617989190cefce9d))

## [0.32.2](https://github.com/BLSQ/openhexa-frontend/compare/0.32.1...0.32.2) (2023-07-04)


### Bug Fixes

* Bring more fixes on FormSection & Apollo caching ([40188ef](https://github.com/BLSQ/openhexa-frontend/commit/40188ef45d848034ac8d6324668308b262cf4f72))


### Miscellaneous

* **Backoff:** Implement a backoff mechanism to retrieve the run status ([#361](https://github.com/BLSQ/openhexa-frontend/issues/361)) ([98ab635](https://github.com/BLSQ/openhexa-frontend/commit/98ab6354815714d4ef351e1ebfee9fafc77ddaa3))

## [0.32.1](https://github.com/BLSQ/openhexa-frontend/compare/0.32.0...0.32.1) (2023-07-03)


### Bug Fixes

* **Connections:** Remove the badge on the card and display it as a subtitle ([#356](https://github.com/BLSQ/openhexa-frontend/issues/356)) ([c2499b3](https://github.com/BLSQ/openhexa-frontend/commit/c2499b328242cc0fb5e98e35304f84ce22603736))
* **Pipelines:** Various fixes ([0540ccd](https://github.com/BLSQ/openhexa-frontend/commit/0540ccd9ddf6a9643b6cd8c04fe7ef812272f6c5))

## [0.32.0](https://github.com/BLSQ/openhexa-frontend/compare/0.31.6...0.32.0) (2023-06-28)


### Features

* **Pipelines:** mail notifications for pipelines ([#339](https://github.com/BLSQ/openhexa-frontend/issues/339)) ([02be4fb](https://github.com/BLSQ/openhexa-frontend/commit/02be4fb7b76e869f8db849c68fc329cdd9242109))

## [0.31.6](https://github.com/BLSQ/openhexa-frontend/compare/0.31.5...0.31.6) (2023-06-26)


### Bug Fixes

* **Files:** The download of an object happens with a content-disposition:download ([#349](https://github.com/BLSQ/openhexa-frontend/issues/349)) ([394396b](https://github.com/BLSQ/openhexa-frontend/commit/394396bd4f31d87aacd4e10641f52eca951680ac))


### Miscellaneous

* **Sidebar:** Visual improvements on how we display the workspaces ([#350](https://github.com/BLSQ/openhexa-frontend/issues/350)) ([9036a1a](https://github.com/BLSQ/openhexa-frontend/commit/9036a1a907fdd2ecafb7894a41774667fa796ed7))

## [0.31.5](https://github.com/BLSQ/openhexa-frontend/compare/0.31.4...0.31.5) (2023-06-26)


### Bug Fixes

* add missing translations ([acedcb6](https://github.com/BLSQ/openhexa-frontend/commit/acedcb66a123e9a94cb2271d69a85216294087b6))
* **RunPipeline:** Bool parameters are never required ([#353](https://github.com/BLSQ/openhexa-frontend/issues/353)) ([8626a50](https://github.com/BLSQ/openhexa-frontend/commit/8626a505d3676172b8210da69c9429a8142102af))
* typo in RunPipelineDialog ([40ef996](https://github.com/BLSQ/openhexa-frontend/commit/40ef996692a79603916f0d32e4dd47ba158b0ceb))

## [0.31.4](https://github.com/BLSQ/openhexa-frontend/compare/0.31.3...0.31.4) (2023-06-23)


### Bug Fixes

* **Files:** Do not display the target directory ([#347](https://github.com/BLSQ/openhexa-frontend/issues/347)) ([3665399](https://github.com/BLSQ/openhexa-frontend/commit/3665399b2d7054160d3630c1bce14b4e7c660da3))
* **Pipelines:** only validate required params ([#346](https://github.com/BLSQ/openhexa-frontend/issues/346)) ([e42a7af](https://github.com/BLSQ/openhexa-frontend/commit/e42a7aff5c7e5936a2727d13acba8b738dece99d))

## [0.31.3](https://github.com/BLSQ/openhexa-frontend/compare/0.31.2...0.31.3) (2023-06-21)


### Bug Fixes

* **Pipelines:** add comparator function for parameters with choices ([#345](https://github.com/BLSQ/openhexa-frontend/issues/345)) ([720e9c8](https://github.com/BLSQ/openhexa-frontend/commit/720e9c80b18e6792c79ea5b06eb895006c84373f))
* **Pipelines:** display error only after when a form field is edited ([#343](https://github.com/BLSQ/openhexa-frontend/issues/343)) ([f74fac2](https://github.com/BLSQ/openhexa-frontend/commit/f74fac2c67fff5c1be70a51d7f20997ae845ac0d))
* **Run:** Poll the status of the run if it's queued or in progress ([#342](https://github.com/BLSQ/openhexa-frontend/issues/342)) ([3960afe](https://github.com/BLSQ/openhexa-frontend/commit/3960afefc88d20539fc9e95fbe0c8045ce182122))


### Miscellaneous

* **Connections:** change label for GCS buckets ([#341](https://github.com/BLSQ/openhexa-frontend/issues/341)) ([8571a5a](https://github.com/BLSQ/openhexa-frontend/commit/8571a5a8b92b862c19ca460e16c3076d71e0e8bc))

## [0.31.2](https://github.com/BLSQ/openhexa-frontend/compare/0.31.1...0.31.2) (2023-06-20)


### Bug Fixes

* **Pipelines:** validate form data before submit ([#332](https://github.com/BLSQ/openhexa-frontend/issues/332)) ([ab912ff](https://github.com/BLSQ/openhexa-frontend/commit/ab912ff179cdf3ab66fd032ec46daa9ba2c5ddee))
* **RunPipeline:** Default value for textarea & fix required prop ([a073fc2](https://github.com/BLSQ/openhexa-frontend/commit/a073fc26824374f8f1a0f093522163502fc8f805))
* **Table:** Remove flicker when changing order by or page ([2ef3761](https://github.com/BLSQ/openhexa-frontend/commit/2ef37612265cee26ce32122cb8a74056674fcb96))

## [0.31.1](https://github.com/BLSQ/openhexa-frontend/compare/0.31.0...0.31.1) (2023-06-15)


### Miscellaneous

* Remove console.log & fix erorr in dev mode ([#334](https://github.com/BLSQ/openhexa-frontend/issues/334)) ([8a1d695](https://github.com/BLSQ/openhexa-frontend/commit/8a1d695f80f641aba5878ed51515d0441832e01f))

## [0.31.0](https://github.com/BLSQ/openhexa-frontend/compare/0.30.2...0.31.0) (2023-06-13)


### Features

* **Connections:** add IASO connection type ([#329](https://github.com/BLSQ/openhexa-frontend/issues/329)) ([88d059e](https://github.com/BLSQ/openhexa-frontend/commit/88d059e8460d74f9d50c8bdb04e9a71034cdbfc5))
* **Database:** User can view all data inside a table and order on the columns ([#330](https://github.com/BLSQ/openhexa-frontend/issues/330)) ([6de4214](https://github.com/BLSQ/openhexa-frontend/commit/6de4214a4512a712442800371ea28bae1432f057))


### Miscellaneous

* **Workspaces:** update database and connections usage sections links ([#328](https://github.com/BLSQ/openhexa-frontend/issues/328)) ([124b7db](https://github.com/BLSQ/openhexa-frontend/commit/124b7dbdfb6156ceed1638d4e77ff0e5e98fdc89))

## [0.30.2](https://github.com/BLSQ/openhexa-frontend/compare/0.30.1...0.30.2) (2023-06-08)


### Bug Fixes

* **Pipelines:** parse float/int parameter to string for select ([#324](https://github.com/BLSQ/openhexa-frontend/issues/324)) ([c420381](https://github.com/BLSQ/openhexa-frontend/commit/c420381c604d380830d1086e084cb3b91a82d33e))
* **Pipelines:** validate all pipeline parameters ([#322](https://github.com/BLSQ/openhexa-frontend/issues/322)) ([53451c2](https://github.com/BLSQ/openhexa-frontend/commit/53451c25df3de2b76651415e9f784e593c063264))
* **Sentry:** Add an ErrorBoundary wrapping nextjs app ([#325](https://github.com/BLSQ/openhexa-frontend/issues/325)) ([2558f4d](https://github.com/BLSQ/openhexa-frontend/commit/2558f4dc76a74097dc44ae21134cc1fb34892a95))


### Miscellaneous

* **Pipelines:** Fetch latest version on dialog opening, do not display the version picker by default ([#310](https://github.com/BLSQ/openhexa-frontend/issues/310)) ([3da5078](https://github.com/BLSQ/openhexa-frontend/commit/3da507889ed8573d47dd7a8f6aeac8ec19f11ce6))

## [0.30.1](https://github.com/BLSQ/openhexa-frontend/compare/0.30.0...0.30.1) (2023-06-05)


### Bug Fixes

* **Apollo:** Set next fetch policy to "cache-and-network" ([#321](https://github.com/BLSQ/openhexa-frontend/issues/321)) ([7039a2d](https://github.com/BLSQ/openhexa-frontend/commit/7039a2d631abf4ab3dfaf219b5d78006d002b782))
* **notebooks:** Wait for the notebook server to be ready before displaying it ([77ddddd](https://github.com/BLSQ/openhexa-frontend/commit/77ddddd823eef0215019554463931fa5b5652caa))
* **notebooks:** Wait for the notebook server to be ready before displaying the iframe ([#320](https://github.com/BLSQ/openhexa-frontend/issues/320)) ([77ddddd](https://github.com/BLSQ/openhexa-frontend/commit/77ddddd823eef0215019554463931fa5b5652caa))
* **Pipelines:** fix issues with parameters ([#314](https://github.com/BLSQ/openhexa-frontend/issues/314)) ([17cffcd](https://github.com/BLSQ/openhexa-frontend/commit/17cffcd6c85529fed296200bba1a4172ae0b6514))
* **Workspace:** Add window titles to workspace pages ([#317](https://github.com/BLSQ/openhexa-frontend/issues/317)) ([7221817](https://github.com/BLSQ/openhexa-frontend/commit/7221817e92765dedea0492e4d7b62b7511a26fa8))


### Miscellaneous

* **deps:** Update Sentry and a few other deps ([d5bb19d](https://github.com/BLSQ/openhexa-frontend/commit/d5bb19d2d1ae255563db9db4190a900edaee3f42))
* **Release:** Add chore commits to changelog ([8f7d610](https://github.com/BLSQ/openhexa-frontend/commit/8f7d610908939f556baf50915ada6aa79b5e4f8f))

## [0.30.0](https://github.com/BLSQ/openhexa-frontend/compare/0.29.1...0.30.0) (2023-05-25)


### Features

* **Workspaces:** restrict workspace creation to superuser ([#308](https://github.com/BLSQ/openhexa-frontend/issues/308)) ([5ad2ff4](https://github.com/BLSQ/openhexa-frontend/commit/5ad2ff43e4a26306a7b5b8066b57fd9f42b4bca6))


### Bug Fixes

* **Pipelines:** enable pagination on versions list ([#311](https://github.com/BLSQ/openhexa-frontend/issues/311)) ([72f61f5](https://github.com/BLSQ/openhexa-frontend/commit/72f61f512373c6232fdc3b25ca52ddaee212d39c))
* **Pipelines:** fix guide URL ([#312](https://github.com/BLSQ/openhexa-frontend/issues/312)) ([7768e2c](https://github.com/BLSQ/openhexa-frontend/commit/7768e2c3d38b7cf6f4cf7321358cea239adf6809))
* **Pipelines:** fix issue with redirection on pipeline run ([#313](https://github.com/BLSQ/openhexa-frontend/issues/313)) ([a5388f0](https://github.com/BLSQ/openhexa-frontend/commit/a5388f02d431072d23f791b78d6486cc493a1540))

## [0.29.1](https://github.com/BLSQ/openhexa-frontend/compare/0.29.0...0.29.1) (2023-05-23)


### Bug Fixes

* **Connections:** remove copy to clipboard button ([#306](https://github.com/BLSQ/openhexa-frontend/issues/306)) ([828b337](https://github.com/BLSQ/openhexa-frontend/commit/828b337c5778a4125b4e7ddfccd6c30a97e0ce23))

## [0.29.0](https://github.com/BLSQ/openhexa-frontend/compare/0.28.0...0.29.0) (2023-05-23)


### Features

* **Workspaces:** hide connections/database parameters  for viewers ([#303](https://github.com/BLSQ/openhexa-frontend/issues/303)) ([85d5ae7](https://github.com/BLSQ/openhexa-frontend/commit/85d5ae71dcacf3651a355e2b88dd7962987300bc))


### Bug Fixes

* **Pipelines:** set pipeline card title to 80% ([#305](https://github.com/BLSQ/openhexa-frontend/issues/305)) ([4ebbcbd](https://github.com/BLSQ/openhexa-frontend/commit/4ebbcbd68fa277e566d775ef22ab915cb7eb5654))

## [0.28.0](https://github.com/BLSQ/openhexa-frontend/compare/0.27.0...0.28.0) (2023-05-22)


### Features

* **Database:** add copy to clipboard on connection parameters ([#300](https://github.com/BLSQ/openhexa-frontend/issues/300)) ([f3c6734](https://github.com/BLSQ/openhexa-frontend/commit/f3c673467ea65e302ff0679c853dc611a0ddf10a))
* **Workspaces:** add copy to clipboard button to fields ([f3c6734](https://github.com/BLSQ/openhexa-frontend/commit/f3c673467ea65e302ff0679c853dc611a0ddf10a))


### Bug Fixes

* **Workspaces:** allow access to only users with workspaces feature ([#298](https://github.com/BLSQ/openhexa-frontend/issues/298)) ([2a7f19b](https://github.com/BLSQ/openhexa-frontend/commit/2a7f19bd7a7a7c5d32cd27b0affe6950f985c64b))
* **Workspaces:** prevent admin from updating/deleting his membership ([#301](https://github.com/BLSQ/openhexa-frontend/issues/301)) ([55abfe2](https://github.com/BLSQ/openhexa-frontend/commit/55abfe2324ea42de9c8f69263911ed087842aa48))

## [0.27.0](https://github.com/BLSQ/openhexa-frontend/compare/0.26.4...0.27.0) (2023-05-19)


### Features

* **Pipelines:** delete pipeline version ([#297](https://github.com/BLSQ/openhexa-frontend/issues/297)) ([b124741](https://github.com/BLSQ/openhexa-frontend/commit/b1247414737e3babb0a8ec7dcff848725113be06))
* **Workspaces:** usage sections simplification ([#295](https://github.com/BLSQ/openhexa-frontend/issues/295)) ([1372b25](https://github.com/BLSQ/openhexa-frontend/commit/1372b25d8ad5cf19a4bece6d294308bb3ed63bc2))

## [0.26.4](https://github.com/BLSQ/openhexa-frontend/compare/0.26.3...0.26.4) (2023-05-11)


### Bug Fixes

* **Pipelines:** Increase size of the run dialog ([e5ddded](https://github.com/BLSQ/openhexa-frontend/commit/e5ddded8c5fd327bbdda6e5e569b4ab7218d03b3))
* **Sidebar:** in compact mode it should not be possible to focus the tooltip ([58ad451](https://github.com/BLSQ/openhexa-frontend/commit/58ad45140bc69df18391b28fe4321b2895ca04bf))

## [0.26.3](https://github.com/BLSQ/openhexa-frontend/compare/0.26.2...0.26.3) (2023-05-11)


### Bug Fixes

* **Pipelines:** replace Select widget by textarea ([fd8016d](https://github.com/BLSQ/openhexa-frontend/commit/fd8016d487f93265239e3fe6972431cca72f6340))
* **Pipelines:** Set a bigger negative margin & padding to not crop the ring around inputs ([f2bfe4d](https://github.com/BLSQ/openhexa-frontend/commit/f2bfe4d0244c9a1628285318bd85309f5a260643))

## [0.26.2](https://github.com/BLSQ/openhexa-frontend/compare/0.26.1...0.26.2) (2023-05-09)


### Bug Fixes

* **Dialog:** Increase the z-index of the dialog container ([591bddb](https://github.com/BLSQ/openhexa-frontend/commit/591bddba361c886e95526cc7bf47f8b506148b13))
* **Layout:** Sidebar background continues on scroll ([591bddb](https://github.com/BLSQ/openhexa-frontend/commit/591bddba361c886e95526cc7bf47f8b506148b13))
* **Members:** Do not display edit buttons if user has not the permission ([591bddb](https://github.com/BLSQ/openhexa-frontend/commit/591bddba361c886e95526cc7bf47f8b506148b13))
* **Workspace:** Hide countries property if empty ([591bddb](https://github.com/BLSQ/openhexa-frontend/commit/591bddba361c886e95526cc7bf47f8b506148b13))
* **Workspaces:** Various fixes based on MJL feedback ([591bddb](https://github.com/BLSQ/openhexa-frontend/commit/591bddba361c886e95526cc7bf47f8b506148b13))

## [0.26.1](https://github.com/BLSQ/openhexa-frontend/compare/0.26.0...0.26.1) (2023-05-09)


### Bug Fixes

* **Catalog:** add displayValue function ([#285](https://github.com/BLSQ/openhexa-frontend/issues/285)) ([f4748ee](https://github.com/BLSQ/openhexa-frontend/commit/f4748ee90f06a0591764f58ebdb4224b941d96c6))
* **Pipelines:** change create by add when typing a string on run dialog ([#283](https://github.com/BLSQ/openhexa-frontend/issues/283)) ([26d6691](https://github.com/BLSQ/openhexa-frontend/commit/26d669138915694856e0a9b26e15ed8f8316ecec))

## [0.26.0](https://github.com/BLSQ/openhexa-frontend/compare/0.25.0...0.26.0) (2023-05-04)


### Features

* **Workspaces:** rename and add check on exit preview button  ([#281](https://github.com/BLSQ/openhexa-frontend/issues/281)) ([160b595](https://github.com/BLSQ/openhexa-frontend/commit/160b59539523c862d834628b39cb74aa909f97dd))


### Bug Fixes

* **Pipelines:** Break long workspace slug in CreatePipelineDialog ([#284](https://github.com/BLSQ/openhexa-frontend/issues/284)) ([422aa92](https://github.com/BLSQ/openhexa-frontend/commit/422aa922f2cf0f9a75495895dc4352189ff19c54))

## [0.25.0](https://github.com/BLSQ/openhexa-frontend/compare/0.24.1...0.25.0) (2023-04-28)


### Features

* **Workspaces:** remove non-functional tabs in settings ([#279](https://github.com/BLSQ/openhexa-frontend/issues/279)) ([f0d7cb7](https://github.com/BLSQ/openhexa-frontend/commit/f0d7cb79022be4068c17f86b5d4c85a559eb2310))
* **Workspaces:** User can close/open the sidebar to have more room By default it shinks the sidebar on the notebooks page ([82884dd](https://github.com/BLSQ/openhexa-frontend/commit/82884dd3ae4a982fdc0596ad84528e8294e9128d))


### Bug Fixes

* **Pipelines:** order pipeline runs by last execution date ([#276](https://github.com/BLSQ/openhexa-frontend/issues/276)) ([d8114b1](https://github.com/BLSQ/openhexa-frontend/commit/d8114b1bce3dfd42ee79ce93c05c27803b0892bc))
* **Pipelines:** Take the values from run to execute again; fix display of 'multiple' type parameter ([82884dd](https://github.com/BLSQ/openhexa-frontend/commit/82884dd3ae4a982fdc0596ad84528e8294e9128d))

## [0.24.1](https://github.com/BLSQ/openhexa-frontend/compare/0.24.0...0.24.1) (2023-04-25)


### Miscellaneous Chores

* release 0.24.1 ([a71e655](https://github.com/BLSQ/openhexa-frontend/commit/a71e655833b2182fd8169bc41f65c455e4679c46))

## [0.24.0](https://github.com/BLSQ/openhexa-frontend/compare/0.23.0...0.24.0) (2023-04-19)


### Features

* **Connections:** use default size for delete button ([#269](https://github.com/BLSQ/openhexa-frontend/issues/269)) ([8a794f5](https://github.com/BLSQ/openhexa-frontend/commit/8a794f56109047df373723aa6258258c31a03453))


### Bug Fixes

* **Connection:** change user field label ([#266](https://github.com/BLSQ/openhexa-frontend/issues/266)) ([be33a4f](https://github.com/BLSQ/openhexa-frontend/commit/be33a4fc618476283a146873f471064528557a19))
* **Database:** fix bad url in database usage snippets ([#271](https://github.com/BLSQ/openhexa-frontend/issues/271)) ([bc0ccf9](https://github.com/BLSQ/openhexa-frontend/commit/bc0ccf901156ab44aab1218fe2f8f769b14ef3cf))
* **Workspaces:** hide administration link for non admin/staff user ([#267](https://github.com/BLSQ/openhexa-frontend/issues/267)) ([6c7614c](https://github.com/BLSQ/openhexa-frontend/commit/6c7614cbad810f41514eb94db5eed143a82a3791))

## [0.23.0](https://github.com/BLSQ/openhexa-frontend/compare/0.22.0...0.23.0) (2023-04-12)


### Features

* **Connections:** display connection env variables ([#264](https://github.com/BLSQ/openhexa-frontend/issues/264)) ([e2d371d](https://github.com/BLSQ/openhexa-frontend/commit/e2d371d15168731d0e810df6d4e5850d779d3980))
* **Workspaces:** redirect to workspaces users without openhexa_legac… ([#257](https://github.com/BLSQ/openhexa-frontend/issues/257)) ([23666af](https://github.com/BLSQ/openhexa-frontend/commit/23666afd18e2f9c34e76b1828ee7079b723c8847))


### Bug Fixes

* **Connections:** add sqlAlchemy and R snippets ([#261](https://github.com/BLSQ/openhexa-frontend/issues/261)) ([2fabe81](https://github.com/BLSQ/openhexa-frontend/commit/2fabe81c1eea5bfad25d1d9a82452c2a4014d201))
* **Workspaces:** Do not display cancel button on /workpaces page ([#265](https://github.com/BLSQ/openhexa-frontend/issues/265)) ([0b602d1](https://github.com/BLSQ/openhexa-frontend/commit/0b602d138e847b83f4b7ae2f97d40a4805a37a97))
* **Workspaces:** last visited workspace may be empty OPENHEXA-Q1 ([#259](https://github.com/BLSQ/openhexa-frontend/issues/259)) ([bea3dc1](https://github.com/BLSQ/openhexa-frontend/commit/bea3dc10e417820e3c0dd0b4afb104ca75403db6))

## [0.22.0](https://github.com/BLSQ/openhexa-frontend/compare/0.21.3...0.22.0) (2023-04-04)


### Features

* **Workspaces:** archive workspace ([#240](https://github.com/BLSQ/openhexa-frontend/issues/240)) ([440433d](https://github.com/BLSQ/openhexa-frontend/commit/440433d0ceabd1bb3667e6f07ec8012e09f92214))
* **Workspaces:** Improve the layout of the outputs on the pipeline run page ([31881f2](https://github.com/BLSQ/openhexa-frontend/commit/31881f26ecc6b78cdda665d909e9b2a8f905489d))
* **Workspaces:** Redirect user to latest workspace seen on this browser on /workspaces ([7bcfeb6](https://github.com/BLSQ/openhexa-frontend/commit/7bcfeb6fb5ca6e03a581e854612bdefc3c3803f9))

## [0.21.3](https://github.com/BLSQ/openhexa-frontend/compare/0.21.2...0.21.3) (2023-03-30)


### Bug Fixes

* **Pipelines:** Hide description if it's empty, fix save button on pi… ([#252](https://github.com/BLSQ/openhexa-frontend/issues/252)) ([baff563](https://github.com/BLSQ/openhexa-frontend/commit/baff5632ed63282f7e060d06579dbaf0dc3d081f))
* **Pipelines:** Hide description if it's empty, fix save button on pipeline ([baff563](https://github.com/BLSQ/openhexa-frontend/commit/baff5632ed63282f7e060d06579dbaf0dc3d081f))
* **Workspaces:** Update description in edit dialog when user switch f… ([#250](https://github.com/BLSQ/openhexa-frontend/issues/250)) ([e8e1f70](https://github.com/BLSQ/openhexa-frontend/commit/e8e1f70abfdeff497b919e6a8a122b3b3ba039f3))
* **Workspaces:** Update description in edit dialog when user switch from workspace ([e8e1f70](https://github.com/BLSQ/openhexa-frontend/commit/e8e1f70abfdeff497b919e6a8a122b3b3ba039f3))

## [0.21.2](https://github.com/BLSQ/openhexa-frontend/compare/0.21.1...0.21.2) (2023-03-29)


### Bug Fixes

* **pipelines:** decrease polling interval while in queued + limit hei… ([#247](https://github.com/BLSQ/openhexa-frontend/issues/247)) ([0c7ea34](https://github.com/BLSQ/openhexa-frontend/commit/0c7ea34613f6bf74685880a3c583151adb32b69f))
* **pipelines:** decrease polling interval while in queued + limit height of run dialog + scroll ([0c7ea34](https://github.com/BLSQ/openhexa-frontend/commit/0c7ea34613f6bf74685880a3c583151adb32b69f))

## [0.21.1](https://github.com/BLSQ/openhexa-frontend/compare/0.21.0...0.21.1) (2023-03-28)


### Bug Fixes

* **Workspaces:** Adapt output type; support string choices & required parameter to run a pipeline ([2105365](https://github.com/BLSQ/openhexa-frontend/commit/210536588cdb1c948185ba66fb9f4eb80a8e276b))
* **Workspaces:** Adapt output type; support string choices & required… ([#244](https://github.com/BLSQ/openhexa-frontend/issues/244)) ([2105365](https://github.com/BLSQ/openhexa-frontend/commit/210536588cdb1c948185ba66fb9f4eb80a8e276b))

## [0.21.0](https://github.com/BLSQ/openhexa-frontend/compare/0.20.0...0.21.0) (2023-03-27)


### Features

* **Database:** add warning messages when changing password ([83f8be5](https://github.com/BLSQ/openhexa-frontend/commit/83f8be51ae4980526bb442a80d0fb2f2915e6a70))
* **Workspaces:** Pipelines V2 ([#243](https://github.com/BLSQ/openhexa-frontend/issues/243)) ([0b5802e](https://github.com/BLSQ/openhexa-frontend/commit/0b5802e7ed24418ad491f3c25548a680bdf4675e))

## [0.20.0](https://github.com/BLSQ/openhexa-frontend/compare/0.19.1...0.20.0) (2023-03-14)


### Features

* **Workspaces:** hide notebooks menu entry for user with role VIEWER ([#226](https://github.com/BLSQ/openhexa-frontend/issues/226)) ([e899659](https://github.com/BLSQ/openhexa-frontend/commit/e8996592a33e5841e5a121d0e29fbd688dc0dfe4))


### Bug Fixes

* **Pipelines:** Link on pipeline's runs first column is incorrect ([a8677e6](https://github.com/BLSQ/openhexa-frontend/commit/a8677e6fe58c2ce17916f29952fa076ee1e49b0f))

## [0.19.1](https://github.com/BLSQ/openhexa-frontend/compare/0.19.0...0.19.1) (2023-03-08)


### Bug Fixes

* **Workspaces:** GCS prefix might not exist (only if uploaded from console or google web interface ([a64b999](https://github.com/BLSQ/openhexa-frontend/commit/a64b99903fb60684d3daeb42e2d210b80940856a))
* **workspaces:** Return a 404 if the mock pipeline or run does not exist ([#222](https://github.com/BLSQ/openhexa-frontend/issues/222)) ([d9a5147](https://github.com/BLSQ/openhexa-frontend/commit/d9a51471907538b89a8a5ae7cd2e9e5bff22f9af))

## [0.19.0](https://github.com/BLSQ/openhexa-frontend/compare/0.18.0...0.19.0) (2023-03-07)


### Features

* **Workspaces:** allow admin to regenerate db password ([#217](https://github.com/BLSQ/openhexa-frontend/issues/217)) ([e6ace32](https://github.com/BLSQ/openhexa-frontend/commit/e6ace32c38c8253ded11b26cae348f07d4b0d3ab))
* **Workspaces:** Implement workspace's files system ([b3b5601](https://github.com/BLSQ/openhexa-frontend/commit/b3b560153aaa5fbcfbc6e6f3b59298c43f6f18f2))

## [0.18.0](https://github.com/BLSQ/openhexa-frontend/compare/0.17.1...0.18.0) (2023-02-28)


### Features

* **Workspaces:** Create Workspace Notebooks ([#216](https://github.com/BLSQ/openhexa-frontend/issues/216)) ([f4bf585](https://github.com/BLSQ/openhexa-frontend/commit/f4bf58589334025e59c3a8471bb0ecaf44c4c204))
* **Workspaces:** workspace database exploration ([#200](https://github.com/BLSQ/openhexa-frontend/issues/200)) ([c1036cd](https://github.com/BLSQ/openhexa-frontend/commit/c1036cd24cfb131ab09ca9196f7292d72562f315))

## [0.17.1](https://github.com/BLSQ/openhexa-frontend/compare/0.17.0...0.17.1) (2023-02-20)


### Bug Fixes

* **Hydration:** ignore hydration errors for datetimes ([acb21ba](https://github.com/BLSQ/openhexa-frontend/commit/acb21bac19220b8055b48f30521732567a582575))

## [0.17.0](https://github.com/BLSQ/openhexa-frontend/compare/0.16.3...0.17.0) (2023-02-09)


### Features

* **connections:** Workspace connections ([#193](https://github.com/BLSQ/openhexa-frontend/issues/193)) ([4bf0ac0](https://github.com/BLSQ/openhexa-frontend/commit/4bf0ac061ebf6b8d08a67322234e80b173cfe753))


### Bug Fixes

* **Pipelines:** Move fields from Airflow data & collapse it by default ([#199](https://github.com/BLSQ/openhexa-frontend/issues/199)) ([2e5909a](https://github.com/BLSQ/openhexa-frontend/commit/2e5909a6acb28895e8e63ca01c1b6de9cb40c18a))

## [0.16.3](https://github.com/BLSQ/openhexa-frontend/compare/0.16.2...0.16.3) (2023-01-25)


### Bug Fixes

* Graphql extensions may not be provided ([#191](https://github.com/BLSQ/openhexa-frontend/issues/191)) ([87b796b](https://github.com/BLSQ/openhexa-frontend/commit/87b796b7cae6b8f8e181cead8f0becbf9abc4ba6))

## [0.16.2](https://github.com/BLSQ/openhexa-frontend/compare/0.16.1...0.16.2) (2023-01-25)


### Bug Fixes

* **Graphql:** Define a new scalar (UUID) for graphql objects. ([#186](https://github.com/BLSQ/openhexa-frontend/issues/186)) ([33c3250](https://github.com/BLSQ/openhexa-frontend/commit/33c3250badc84fcce8b90b158ec9a9deed6a4741))

## [0.16.1](https://github.com/BLSQ/openhexa-frontend/compare/0.16.0...0.16.1) (2023-01-25)


### Bug Fixes

* **2fa:** fix typo & add 2fa status on account page ([#188](https://github.com/BLSQ/openhexa-frontend/issues/188)) ([b512ebf](https://github.com/BLSQ/openhexa-frontend/commit/b512ebf493c3c9fb70a1cec68a501cd8ece1749f))

## [0.16.0](https://github.com/BLSQ/openhexa-frontend/compare/0.15.5...0.16.0) (2023-01-24)


### Features

* **2fa:** Add verification step to two factor ([#185](https://github.com/BLSQ/openhexa-frontend/issues/185)) ([2130260](https://github.com/BLSQ/openhexa-frontend/commit/213026017b1a7192f3e0cad7990242bb4992888a))


### Bug Fixes

* **Workspaces:** display warning when user can't create workspace ([#183](https://github.com/BLSQ/openhexa-frontend/issues/183)) ([6ca2d6d](https://github.com/BLSQ/openhexa-frontend/commit/6ca2d6da40c551dd55704697c225e3042a3b45ba))

## [0.15.5](https://github.com/BLSQ/openhexa-frontend/compare/0.15.4...0.15.5) (2023-01-17)


### Bug Fixes

* **server:** Do not proxy urls starting by '/' ([#180](https://github.com/BLSQ/openhexa-frontend/issues/180)) ([6a7fed6](https://github.com/BLSQ/openhexa-frontend/commit/6a7fed6e10ab57e922661d531db837a252eb952d))

## [0.15.4](https://github.com/BLSQ/openhexa-frontend/compare/0.15.3...0.15.4) (2023-01-17)


### Bug Fixes

* **Workspaces:** Mock unimplemented features for workspaces ([2c24a1e](https://github.com/BLSQ/openhexa-frontend/commit/2c24a1eee1f96209cfa7893c3a44c58e31466731))

## [0.15.3](https://github.com/BLSQ/openhexa-frontend/compare/0.15.2...0.15.3) (2023-01-16)


### Bug Fixes

* **Workspaces:** check workspace featureFlag and permission on server… ([#174](https://github.com/BLSQ/openhexa-frontend/issues/174)) ([5456999](https://github.com/BLSQ/openhexa-frontend/commit/5456999d7f964ffca6e1de0c4887ca39bab87c2f))

## [0.15.2](https://github.com/BLSQ/openhexa-frontend/compare/0.15.1...0.15.2) (2023-01-16)


### Bug Fixes

* **2FA:** User is not redirected to login page after activation ([6e8abfd](https://github.com/BLSQ/openhexa-frontend/commit/6e8abfd3c612d75b1d73a1279ba1d8f74ede070d))
* **2FA:** User is not redirected to login page after activation ([6e8abfd](https://github.com/BLSQ/openhexa-frontend/commit/6e8abfd3c612d75b1d73a1279ba1d8f74ede070d))

## [0.15.1](https://github.com/BLSQ/openhexa-frontend/compare/0.15.0...0.15.1) (2023-01-16)


### Bug Fixes

* **2FA:** Fix send new token on login page ([#170](https://github.com/BLSQ/openhexa-frontend/issues/170)) ([fb77a66](https://github.com/BLSQ/openhexa-frontend/commit/fb77a667e2f7a69ee58cc565650a5c8793c938a8))

## [0.15.0](https://github.com/BLSQ/openhexa-frontend/compare/0.14.1...0.15.0) (2023-01-16)


### Features

* **2FA:** Setup two factor authentication on the frontend ([876fae7](https://github.com/BLSQ/openhexa-frontend/commit/876fae72cdeaab49a8e34e48cf3e51caa59594ec))
* **2FA:** Setup two factor authentication on the frontend ([876fae7](https://github.com/BLSQ/openhexa-frontend/commit/876fae72cdeaab49a8e34e48cf3e51caa59594ec))
* **Workspaces:** Invite member, update workspace ([aa080b7](https://github.com/BLSQ/openhexa-frontend/commit/aa080b780f53ccd1c19521eef4c7c1d9ca978d5f))


### Bug Fixes

* **Header:** Auto-close menu on header on click ([6b8cead](https://github.com/BLSQ/openhexa-frontend/commit/6b8ceadcd29cba91b586e67f70d42c183976a5e4))

## [0.14.1](https://github.com/BLSQ/openhexa-frontend/compare/0.14.0...0.14.1) (2022-12-15)


### Bug Fixes

* More realistic fixtures ([#156](https://github.com/BLSQ/openhexa-frontend/issues/156)) ([99981ca](https://github.com/BLSQ/openhexa-frontend/commit/99981ca3f1a5253e41a934395047df3c97e5126c))

## [0.14.0](https://github.com/BLSQ/openhexa-frontend/compare/0.13.2...0.14.0) (2022-12-13)


### Miscellaneous Chores

* release 0.14.0 ([11abb9b](https://github.com/BLSQ/openhexa-frontend/commit/11abb9bccb6392a89005abb847a1d2d0cc2c33ff))

## [0.13.2](https://github.com/BLSQ/openhexa-frontend/compare/0.13.1...0.13.2) (2022-12-12)


### Bug Fixes

* load favicon file ([#151](https://github.com/BLSQ/openhexa-frontend/issues/151)) ([ac99af0](https://github.com/BLSQ/openhexa-frontend/commit/ac99af04850793275662c1ca701f2e3c55e4925e))
* **Logout:** Logout has to be done using the page on django ([#144](https://github.com/BLSQ/openhexa-frontend/issues/144)) ([517a456](https://github.com/BLSQ/openhexa-frontend/commit/517a456a97049286897114ded36d7b6ac270567a))
* **Pipelines:** Display an error when user types an invalid json configuration ([#145](https://github.com/BLSQ/openhexa-frontend/issues/145)) ([d63ed22](https://github.com/BLSQ/openhexa-frontend/commit/d63ed229e3fad233eda3550138b6489379e2514a))

## [0.13.1](https://github.com/BLSQ/openhexa-frontend/compare/0.13.0...0.13.1) (2022-11-29)


### Bug Fixes

* Include workspaces changes ([0f751c2](https://github.com/BLSQ/openhexa-frontend/commit/0f751c298fcdb883fb2ef6a060a749c4a7696fac))

## [0.13.0](https://github.com/BLSQ/openhexa-frontend/compare/0.12.7...0.13.0) (2022-11-29)


### Features

* Release of the workspace prototype ([4a79b22](https://github.com/BLSQ/openhexa-frontend/commit/4a79b22f2aa9134184178373d9cbf0613bfb6123))

## [0.12.7](https://github.com/BLSQ/openhexa-frontend/compare/0.12.6...0.12.7) (2022-11-16)


### Bug Fixes

* Pass props by name directly to LinkColumn ([e881473](https://github.com/BLSQ/openhexa-frontend/commit/e881473183f4f5290b922c7860d6a3b550b516ac))

## [0.12.6](https://github.com/BLSQ/openhexa-frontend/compare/0.12.5...0.12.6) (2022-11-14)


### Bug Fixes

* **PipelinesRun:** Only display re-run action when job is finished ([ce85ea1](https://github.com/BLSQ/openhexa-frontend/commit/ce85ea12675b2beebbbaad72e4df3bda7ee72c1a))
* **Title:** add missing titles on search and notebooks page ([38d69a0](https://github.com/BLSQ/openhexa-frontend/commit/38d69a0c1125eebaac6a7904d830160124f88a09))

## [0.12.5](https://github.com/BLSQ/openhexa-frontend/compare/0.12.4...0.12.5) (2022-11-14)


### Bug Fixes

* **Login:** Use path instead of url to match urls handled by the frontend and the ones handled by the backend. ([0dc9fe1](https://github.com/BLSQ/openhexa-frontend/commit/0dc9fe1fe54896b5fe1757a391b4d2daa32cb345))
* **Pipelines:** add pagination on dag run messages table ([37c4d28](https://github.com/BLSQ/openhexa-frontend/commit/37c4d284b825dacad53f1e6879b665c438df718c))
* **TextColumn:** Truncate correctly the text ([9032aef](https://github.com/BLSQ/openhexa-frontend/commit/9032aef96d6ff11c600181bc64f7e0de29ee0468))

## [0.12.4](https://github.com/BLSQ/openhexa-frontend/compare/0.12.3...0.12.4) (2022-11-09)


### Bug Fixes

* **Visualizations:** fix breadcrumb text and redirect url ([546fc5a](https://github.com/BLSQ/openhexa-frontend/commit/546fc5a7e52a478b91f1b33f620a9007af804cfd))

## [0.12.3](https://github.com/BLSQ/openhexa-frontend/compare/0.12.2...0.12.3) (2022-11-07)


### Bug Fixes

* **Sentry:** Do not record /ready transactions ([56a1e80](https://github.com/BLSQ/openhexa-frontend/commit/56a1e807c2d2defd1ed3b36267955110e7af1dc7))

## [0.12.2](https://github.com/BLSQ/openhexa-frontend/compare/0.12.1...0.12.2) (2022-11-07)


### Bug Fixes

* **Time:** Ignore hydration issues  with the Time component ([bb2854b](https://github.com/BLSQ/openhexa-frontend/commit/bb2854be65407a2762f15ef16d3ded2574509935))

## [0.12.0](https://github.com/BLSQ/openhexa-frontend/compare/0.11.0...0.12.0) (2022-11-07)


### Features

* **Account:** Add the user's account page ([fe49745](https://github.com/BLSQ/openhexa-frontend/commit/fe497457ac7ebdfb8e3822388b90322337ff20f5))

## [0.11.0](https://github.com/BLSQ/openhexa-frontend/compare/0.10.2...0.11.0) (2022-11-03)


### Features

* **Permissions:** New permissions system ([#101](https://github.com/BLSQ/openhexa-frontend/issues/101)) ([e062bc2](https://github.com/BLSQ/openhexa-frontend/commit/e062bc2ed78a2469eca1a64b1f2a748f08029d7c))

## [0.10.2](https://github.com/BLSQ/openhexa-frontend/compare/0.10.1...0.10.2) (2022-10-28)


### Bug Fixes

* **i18n:** DO not redirect to /fr when requesting / ([#102](https://github.com/BLSQ/openhexa-frontend/issues/102)) ([65a8c07](https://github.com/BLSQ/openhexa-frontend/commit/65a8c07035b4aa4ceb4ab9c6f79af1907c62c7d4))

## [0.10.1](https://github.com/BLSQ/openhexa-frontend/compare/0.10.0...0.10.1) (2022-10-19)


### Bug Fixes

* **Pipelines:** Only display "open in airflow" link if user is admin ([407cd16](https://github.com/BLSQ/openhexa-frontend/commit/407cd165cd4ded5eef3fd173cd7e1ec55d274108))

## [0.10.0](https://github.com/BLSQ/openhexa-frontend/compare/0.9.4...0.10.0) (2022-10-18)


### Features

* **Favorite:** User can mark runs as favorite ([a2ccb73](https://github.com/BLSQ/openhexa-frontend/commit/a2ccb73e224bb9cb9332517aa56453dbdf672fa5))


### Bug Fixes

* **Collections:** Country badge follows the badge while scrolling in a dialog ([3dcf52e](https://github.com/BLSQ/openhexa-frontend/commit/3dcf52eb7c7a1b1f95e0131d66550528033f6f2a))
* **Header:** User can open quicksearch & use cmd+k to open it ([456432b](https://github.com/BLSQ/openhexa-frontend/commit/456432b4408194e093143bfbc36ea1b42ec2ea10))
* **Pipelines:** User can go to airflow from a pipeline or a pipeline run ([8e64495](https://github.com/BLSQ/openhexa-frontend/commit/8e64495c628c35763c3fb3dc46f65db7b7d8e9e1))

## [0.9.4](https://github.com/BLSQ/openhexa-frontend/compare/0.9.3...0.9.4) (2022-10-13)


### Bug Fixes

* **Quicksearch:** Directly closes when user clicks on 'add' on a collection page' ([f9a0ce2](https://github.com/BLSQ/openhexa-frontend/commit/f9a0ce2968cc8b814673e4195cfa9628e1362ef8))

## [0.9.3](https://github.com/BLSQ/openhexa-frontend/compare/0.9.2...0.9.3) (2022-10-12)


### Bug Fixes

* **Quicksearch:** DO not open the quicksearch on every page ([a66f9ee](https://github.com/BLSQ/openhexa-frontend/commit/a66f9ee18991d433ad5211e39e516cf9f58ecb92))

## [0.9.2](https://github.com/BLSQ/openhexa-frontend/compare/0.9.1...0.9.2) (2022-10-07)


### Bug Fixes

* **Search:** Close quicksearch on route change ([1b55be8](https://github.com/BLSQ/openhexa-frontend/commit/1b55be8038c661389d70377d54c477a6ece5cb97))

## [0.9.1](https://github.com/BLSQ/openhexa-frontend/compare/0.9.0...0.9.1) (2022-10-07)


### Bug Fixes

* **Search:** Type select on search page is broken ([3c5beac](https://github.com/BLSQ/openhexa-frontend/commit/3c5beac993c7b78638418a5f8ca4913c804df037))

## [0.9.0](https://github.com/BLSQ/openhexa-frontend/compare/0.8.1...0.9.0) (2022-10-07)


### Features

* **Features:** Add features to schema ([8b286ab](https://github.com/BLSQ/openhexa-frontend/commit/8b286ab36a6c56fc3f98707774c45f86d154bbca))


### Bug Fixes

* **Search:** Increase padding of search input ([6bc63d1](https://github.com/BLSQ/openhexa-frontend/commit/6bc63d1a3159249c012250fb21ab7f2e2f996d45))
* **Sentry:** Get sentry sampling traces rate from env ([718074d](https://github.com/BLSQ/openhexa-frontend/commit/718074d2f7ecae1ea42465a2c58d6bd115f54774))

## [0.8.1](https://github.com/BLSQ/openhexa-frontend/compare/0.8.0...0.8.1) (2022-10-06)


### Bug Fixes

* **Search:** Limit the quicksearch results to 10 entries ([941338c](https://github.com/BLSQ/openhexa-frontend/commit/941338c9f97b056e9f94d005d1f362babf6e4576))

## [0.8.0](https://github.com/BLSQ/openhexa-frontend/compare/0.7.16...0.8.0) (2022-10-06)


### Features

* **Search:** Add search page ([1059452](https://github.com/BLSQ/openhexa-frontend/commit/1059452034e5769a5288b55346f22410e91dcbff))


### Bug Fixes

* **Collections:** Summary was erased on update of the description ([7ccc236](https://github.com/BLSQ/openhexa-frontend/commit/7ccc236f54a64af118eb25c5484c007d305801ee))

## [0.7.16](https://github.com/BLSQ/openhexa-frontend/compare/0.7.15...0.7.16) (2022-10-05)


### Bug Fixes

* **ProgressPie:** Add case for 0 ([8e29d8d](https://github.com/BLSQ/openhexa-frontend/commit/8e29d8d9dac149ed17869eda620581a7ed0a3edd))

## [0.7.15](https://github.com/BLSQ/openhexa-frontend/compare/0.7.14...0.7.15) (2022-10-04)


### Bug Fixes

* **ProgressPie:** Add the progress in text ([d468152](https://github.com/BLSQ/openhexa-frontend/commit/d4681526ed806c086b6fb5a5a81da141f9b5c258))

## [0.7.14](https://github.com/BLSQ/openhexa-frontend/compare/0.7.13...0.7.14) (2022-10-04)


### Bug Fixes

* **Pipelines:** Pagination of pipelines is not working ([ce9bc26](https://github.com/BLSQ/openhexa-frontend/commit/ce9bc26ec2310896b37e069b1f12917b79acf3a8))

## [0.7.13](https://github.com/BLSQ/openhexa-frontend/compare/0.7.12...0.7.13) (2022-09-26)


### Bug Fixes

* **IHP:** Add missing parameter reuse_existing_extract ([3db150c](https://github.com/BLSQ/openhexa-frontend/commit/3db150c1d838af08fd2549bf24ac47b478c58b7f))

## [0.7.12](https://github.com/BLSQ/openhexa-frontend/compare/0.7.11...0.7.12) (2022-09-26)


### Bug Fixes

* **Pipelines:** Small UX improvements on the run page ([a3fbd4e](https://github.com/BLSQ/openhexa-frontend/commit/a3fbd4e5fa9f12f6225ed192685e44e561df73d4))

## [0.7.11](https://github.com/BLSQ/openhexa-frontend/compare/0.7.10...0.7.11) (2022-09-24)


### Bug Fixes

* **Pipelines:** Add condition to display the progress pie ([3ce6c86](https://github.com/BLSQ/openhexa-frontend/commit/3ce6c86c150221b62326d795e465d8ea92ed6af3))

## [0.7.10](https://github.com/BLSQ/openhexa-frontend/compare/0.7.9...0.7.10) (2022-09-24)


### Features

* **Pipelines:** Revamp the pipeline's job page ([9053c88](https://github.com/BLSQ/openhexa-frontend/commit/9053c880b75f84c49b149b2a23753db45f50c51e))

## [0.7.9](https://github.com/BLSQ/openhexa-frontend/compare/0.7.8...0.7.9) (2022-09-23)


### Bug Fixes

* **pipelines:** IHP parameters must be in config.parameters ([aca9afa](https://github.com/BLSQ/openhexa-frontend/commit/aca9afa4ba42cc38c3f8d63c5474cb8481094781))

## [0.7.8](https://github.com/BLSQ/openhexa-frontend/compare/0.7.7...0.7.8) (2022-09-23)


### Bug Fixes

* **IHP:** Set default values for checkbox & use checked={} ([3cd4e94](https://github.com/BLSQ/openhexa-frontend/commit/3cd4e94a7fe141bccbe4eaa401b6c21080f55050))

## [0.7.7](https://github.com/BLSQ/openhexa-frontend/compare/0.7.6...0.7.7) (2022-09-23)


### Bug Fixes

* **Pipelines:** decrease duration of refresh when pipeline is running ([72d1f62](https://github.com/BLSQ/openhexa-frontend/commit/72d1f6265a4b741443572dd9787241068bff4e96))

## [0.7.6](https://github.com/BLSQ/openhexa-frontend/compare/0.7.5...0.7.6) (2022-09-23)


### Bug Fixes

* Redirect old airflow urls to /pipelines ones ([1c33d44](https://github.com/BLSQ/openhexa-frontend/commit/1c33d44e27a6a14a1de280fe2f76af53a31b29d1))

## [0.7.5](https://github.com/BLSQ/openhexa-frontend/compare/0.7.4...0.7.5) (2022-09-22)


### Bug Fixes

* **Header:** Add /admin entry if user is marked as "staff" user ([2e2ac7c](https://github.com/BLSQ/openhexa-frontend/commit/2e2ac7c3c30ba6dc084d9c7cd01d42379186c5e1))

## [0.7.4](https://github.com/BLSQ/openhexa-frontend/compare/0.7.3...0.7.4) (2022-09-22)


### Bug Fixes

* **Pipelines:** Config editor should not shrink ([37e4fef](https://github.com/BLSQ/openhexa-frontend/commit/37e4fef447436e38f2a4061b7eae186c9c4bc59e))

## [0.7.3](https://github.com/BLSQ/openhexa-frontend/compare/0.7.2...0.7.3) (2022-09-22)


### Bug Fixes

* **IHP:** Wrong identifier ([56d305b](https://github.com/BLSQ/openhexa-frontend/commit/56d305bc5940640fb372d6a7a8bab7c1020ab14b))

## [0.7.2](https://github.com/BLSQ/openhexa-frontend/compare/0.7.1...0.7.2) (2022-09-22)


### Miscellaneous Chores

* Release 0.7.2 ([0decade](https://github.com/BLSQ/openhexa-frontend/commit/0decade6257a1349b2c1777d81c18d8bb255d35b))

## [0.7.1](https://github.com/BLSQ/openhexa-frontend/compare/0.7.0...0.7.1) (2022-09-20)


### Features

* **pipelines:** Add outputs ([66d0c7a](https://github.com/BLSQ/openhexa-frontend/commit/66d0c7a834a44f85b63558823563df8d0a04d27b))


### Miscellaneous Chores

* Release 0.7.1 ([06c52b7](https://github.com/BLSQ/openhexa-frontend/commit/06c52b7c03cf08b569918ab3f7a21ecb3c0a7b18))

## [0.7.0](https://github.com/BLSQ/openhexa-frontend/compare/0.6.2...0.7.0) (2022-09-20)


### Miscellaneous Chores

* release 0.7.0 ([72f2be5](https://github.com/BLSQ/openhexa-frontend/commit/72f2be5d3fa481548f99e7b007fc39098daf81e5))

## [0.6.2](https://github.com/BLSQ/openhexa-frontend/compare/0.6.1...0.6.2) (2022-09-09)


### Bug Fixes

* **Collections:** Fix element values extracted from the url and the isInCollection check ([aef7b88](https://github.com/BLSQ/openhexa-frontend/commit/aef7b880dae69807ee0bbad175a6806a6545c84e))

## [0.6.1](https://github.com/BLSQ/openhexa-frontend/compare/0.6.0...0.6.1) (2022-09-09)


### Features

* **Page:** Add a title on pages ([19d0fca](https://github.com/BLSQ/openhexa-frontend/commit/19d0fca56635fb56ad58c31378a86721c4c63ed1))


### Bug Fixes

* **Datagrid:** set max width for CountryColumn & truncate text in TextColumn when wrapped in a link ([c193de5](https://github.com/BLSQ/openhexa-frontend/commit/c193de524c1bf9407cdf914be9b1db55ad45820e))


### Miscellaneous Chores

* **Main:** Release 0.6.1 ([7180291](https://github.com/BLSQ/openhexa-frontend/commit/7180291db836d5d0eca94848e4bf3d7bc57933c5))

## [0.6.0](https://github.com/BLSQ/openhexa-frontend/compare/0.5.3...0.6.0) (2022-09-09)


### Features

* **collections:** User can delete elements from collections directly ([0237e3c](https://github.com/BLSQ/openhexa-frontend/commit/0237e3c5a40a722869f0aee6f6d995e7d134b779))
* **Collection:** User can add & remove elements from collection's page ([47dd5e8](https://github.com/BLSQ/openhexa-frontend/commit/47dd5e816bbb8b99263627ba9d748fce7cd69aa2))
* **Search:** Implement a basic quick search component ([22a881a](https://github.com/BLSQ/openhexa-frontend/commit/22a881ae15311599eaafa040f933630a948b2933))

## [0.5.3](https://github.com/BLSQ/openhexa-frontend/compare/0.5.2...0.5.3) (2022-09-07)


### Features

* **Collections:** Add a summary to the collection ([7e0be54](https://github.com/BLSQ/openhexa-frontend/commit/7e0be54725b854ce45282f28f3ea0e82fd36b70e))


### Bug Fixes

* **Combobox:** ALready bring the "by" prop that will be used to compare value ([7e0be54](https://github.com/BLSQ/openhexa-frontend/commit/7e0be54725b854ce45282f28f3ea0e82fd36b70e))
* **ManageCollections:** Return newly created collection to perform actions on the result. ([7e0be54](https://github.com/BLSQ/openhexa-frontend/commit/7e0be54725b854ce45282f28f3ea0e82fd36b70e))
* **Textarea:** Take full width ([7e0be54](https://github.com/BLSQ/openhexa-frontend/commit/7e0be54725b854ce45282f28f3ea0e82fd36b70e))

## [0.5.2](https://github.com/BLSQ/openhexa-frontend/compare/0.5.1...0.5.2) (2022-09-01)


### Bug Fixes

* **main:** Set a personal access token to be able to trigger docker image build after a release creation ([9e8894d](https://github.com/BLSQ/openhexa-frontend/commit/9e8894dd9767cf1d4d82e1c7a6ce975f2eb0f1eb))

## [0.5.1](https://github.com/BLSQ/openhexa-frontend/compare/0.5.0...0.5.1) (2022-09-01)


### Miscellaneous Chores

* release 0.5.1 ([47c89c9](https://github.com/BLSQ/openhexa-frontend/commit/47c89c9c5f04c1c536a9a4d9b0c16008443ab234))
