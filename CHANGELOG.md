# Changelog

## [0.83.1](https://github.com/BLSQ/openhexa-app/compare/0.83.0...0.83.1) (2025-03-17)


### Bug Fixes

* Datasets files not profiled (HEXA-1219) ([#943](https://github.com/BLSQ/openhexa-app/issues/943)) ([62a7435](https://github.com/BLSQ/openhexa-app/commit/62a74355d5743c0287e2043b29c1c323178fd05e))

## [0.83.0](https://github.com/BLSQ/openhexa-app/compare/0.82.0...0.83.0) (2025-03-03)


### ⚠ BREAKING CHANGES

* Allow creation of a pipeline with a duplicate name  (HEXA-1170) ([#930](https://github.com/BLSQ/openhexa-app/issues/930))

### Features

* Allow creation of a pipeline with a duplicate name  (HEXA-1170) ([#930](https://github.com/BLSQ/openhexa-app/issues/930)) ([531151e](https://github.com/BLSQ/openhexa-app/commit/531151e66a902c7ea85f63cc3bf897e2b50ab433))

## [0.82.0](https://github.com/BLSQ/openhexa-app/compare/0.81.0...0.82.0) (2025-02-28)


### Features

* Embedded dashboards from Superset made right! ([#931](https://github.com/BLSQ/openhexa-app/issues/931)) ([ebc6732](https://github.com/BLSQ/openhexa-app/commit/ebc6732dd9231012a87b822abc44f706e4de453e))
* **Parameter:** HEXA-1136 move name and level to label  for GraphQL DHIS interface ([#938](https://github.com/BLSQ/openhexa-app/issues/938)) ([9898710](https://github.com/BLSQ/openhexa-app/commit/9898710e43f98ac70d88f76698ef3784ff629c33))
* Queue and send analytics asynchronously to MixPanel (HEXA-1191) ([#933](https://github.com/BLSQ/openhexa-app/issues/933)) ([60397d5](https://github.com/BLSQ/openhexa-app/commit/60397d572d675560645c84c07ccd2622e187cfbb))


### Bug Fixes

* handle gracefully duplicate template name (HEXA-1199) ([#936](https://github.com/BLSQ/openhexa-app/issues/936)) ([ed48944](https://github.com/BLSQ/openhexa-app/commit/ed489441a1cd56f97833c6b3c3ac183270584d5e))

## [0.81.0](https://github.com/BLSQ/openhexa-app/compare/0.80.0...0.81.0) (2025-02-14)


### Features

* Management pages for templates (HEXA-1129, HEXA-1130) ([#921](https://github.com/BLSQ/openhexa-app/issues/921)) ([b68411a](https://github.com/BLSQ/openhexa-app/commit/b68411a7961aa63b532a53174bf0b35eafdf3542))
* **workspace:** HEXA-1136, DHIS2 parameter widget from connection ([#926](https://github.com/BLSQ/openhexa-app/issues/926)) ([8129c5a](https://github.com/BLSQ/openhexa-app/commit/8129c5a7787cee6f20a64178a6390256d47e071e))


### Bug Fixes

* **Mails:** Allow the admin to enable SSL for the mail server (in addition of TLS) ([#928](https://github.com/BLSQ/openhexa-app/issues/928)) ([65fb3fc](https://github.com/BLSQ/openhexa-app/commit/65fb3fc134090a8a0c2f1ecf0cbc128c81838c95))

## [0.80.0](https://github.com/BLSQ/openhexa-app/compare/0.79.0...0.80.0) (2025-02-07)


### Features

* Changelog support  for pipeline templates (HEXA-1166) ([#907](https://github.com/BLSQ/openhexa-app/issues/907)) ([0fe67fc](https://github.com/BLSQ/openhexa-app/commit/0fe67fcdcd33cc5944dd3690d6e2aa96c162bb10))

## [0.79.0](https://github.com/BLSQ/openhexa-app/compare/0.78.0...0.79.0) (2025-02-03)


### Features

* handle default parameters values for pipeline template upgrades (HEXA-1165) ([#908](https://github.com/BLSQ/openhexa-app/issues/908)) ([c8d0cdf](https://github.com/BLSQ/openhexa-app/commit/c8d0cdf83f96c9c269860b043a7f3a8348601805))
* instrument and improve feature adoption analytics (HEXA-1156) ([#911](https://github.com/BLSQ/openhexa-app/issues/911)) ([a9ffe7f](https://github.com/BLSQ/openhexa-app/commit/a9ffe7fb9dcadaf3b14099f66f001edba2076a90))


### Bug Fixes

* HEXA-1163 - refactor dhis2 client, move connection to workspace ([#906](https://github.com/BLSQ/openhexa-app/issues/906)) ([50a14a9](https://github.com/BLSQ/openhexa-app/commit/50a14a918671dffd6dfce7be7a713e6aa3becec9))
* Support deleted source pipeline (HEXA-1169) ([#909](https://github.com/BLSQ/openhexa-app/issues/909)) ([097dfef](https://github.com/BLSQ/openhexa-app/commit/097dfef49db64f8a59d39967ed9f3fab17b93836))

## [0.78.0](https://github.com/BLSQ/openhexa-app/compare/0.77.0...0.78.0) (2025-01-22)


### Features

* Fix permissions for Pipeline Templates (HEXA-1121 HEXA-1122 HEXA-1124 HEXA-1125 HEXA-1126 HEXA-1128) ([#903](https://github.com/BLSQ/openhexa-app/issues/903)) ([32c5fad](https://github.com/BLSQ/openhexa-app/commit/32c5fad10d23dcff125eb3d76c212e336bdbf916))
* HEXA-1127 button to create a new version of the pipeline using the new template ([#901](https://github.com/BLSQ/openhexa-app/issues/901)) ([fda8fad](https://github.com/BLSQ/openhexa-app/commit/fda8fad6a289d33884dffbf06985ef9f7b8d4cbd))
* pgAdmin dev tool setup ([#850](https://github.com/BLSQ/openhexa-app/issues/850)) ([193fc32](https://github.com/BLSQ/openhexa-app/commit/193fc32ef914fc50292a37ff29c224b6f034ef4b))

## [0.77.0](https://github.com/BLSQ/openhexa-app/compare/0.76.4...0.77.0) (2025-01-14)


### Features

* **Datasets:** User defined annotations on dataset files #Pathways-157 ([35ca450](https://github.com/BLSQ/openhexa-app/commit/35ca4506bc28ff1a12e89e2d6e6bc2ce7fb953f7))
* Hexa 1117 dhis2 graphql interface ([#888](https://github.com/BLSQ/openhexa-app/issues/888)) ([b72ed47](https://github.com/BLSQ/openhexa-app/commit/b72ed47c48327e43b965dec47147e373a9d8c34f))
* HEXA-1120 template pipelines and template versions models + endpoint to create template ([#874](https://github.com/BLSQ/openhexa-app/issues/874)) ([22ed895](https://github.com/BLSQ/openhexa-app/commit/22ed895f2b31febd1c715ff2bff4eaaf8fc48311))
* HEXA-1122 list of templates in create pipeline dialog ([#885](https://github.com/BLSQ/openhexa-app/issues/885)) ([be8b201](https://github.com/BLSQ/openhexa-app/commit/be8b20168aeb0383d10eb4bbcc333a12c6d60ab2))
* HEXA-1125 endpoint for source template and check if a new template version is available for upgrade ([#890](https://github.com/BLSQ/openhexa-app/issues/890)) ([272e5d4](https://github.com/BLSQ/openhexa-app/commit/272e5d4353cc3c29f72c3652d8c5a03b6169bf48))
* HEXA-1146 Propagate pipeline default parameters in new versions ([#883](https://github.com/BLSQ/openhexa-app/issues/883)) ([6e518f6](https://github.com/BLSQ/openhexa-app/commit/6e518f6b19f90844bc8456eaa645914244a04be9))


### Bug Fixes

* **Mixpanel:** Set a timeout on the mixpanel requests & never retry to send events ([#895](https://github.com/BLSQ/openhexa-app/issues/895)) ([4b60171](https://github.com/BLSQ/openhexa-app/commit/4b60171118c37cc3d6752ab6eed39728c48dca71))
* **Mixpanel:** Set a timeout on the mixpanel requests & never retry to send events ([#897](https://github.com/BLSQ/openhexa-app/issues/897)) ([6f6b9ef](https://github.com/BLSQ/openhexa-app/commit/6f6b9efdf6fac695523aba1ea2ade3fcaf858cec))

## [0.76.4](https://github.com/BLSQ/openhexa-app/compare/0.76.3...0.76.4) (2024-12-16)


### Bug Fixes

* OPENHEXA-1BV snake_case issue in create bucket folder ([#880](https://github.com/BLSQ/openhexa-app/issues/880)) ([d6a3e67](https://github.com/BLSQ/openhexa-app/commit/d6a3e674e1c8f9d6192c97716b357d48bff9293a))

## [0.76.3](https://github.com/BLSQ/openhexa-app/compare/0.76.2...0.76.3) (2024-12-16)


### Bug Fixes

* **Pipelines:** Put back 'number' on PipelineVersion to not break ([#878](https://github.com/BLSQ/openhexa-app/issues/878)) ([417433b](https://github.com/BLSQ/openhexa-app/commit/417433b8a9c39dba0c17425c3a9c35ad5370e3c1))

## [0.76.2](https://github.com/BLSQ/openhexa-app/compare/0.76.1...0.76.2) (2024-12-13)


### Bug Fixes

* **Datasets:** snake case for datasetlink id ([#873](https://github.com/BLSQ/openhexa-app/issues/873)) ([0eb8667](https://github.com/BLSQ/openhexa-app/commit/0eb8667f9017f20ef9eaf23920cb27dde8da1f60))

## [0.76.1](https://github.com/BLSQ/openhexa-app/compare/0.76.0...0.76.1) (2024-12-11)


### Bug Fixes

* **pipeline:** comment env var requirement ([#870](https://github.com/BLSQ/openhexa-app/issues/870)) ([baf2d9f](https://github.com/BLSQ/openhexa-app/commit/baf2d9f1aed9b72fa3b97d11118511179b53f716))

## [0.76.0](https://github.com/BLSQ/openhexa-app/compare/0.75.2...0.76.0) (2024-12-09)


### ⚠ BREAKING CHANGES

* Set a default version number for each pipeline version, make version name optional ([#857](https://github.com/BLSQ/openhexa-app/issues/857))

### Features

* conditionally run pipelines in debug mode ([#862](https://github.com/BLSQ/openhexa-app/issues/862)) ([5120d50](https://github.com/BLSQ/openhexa-app/commit/5120d509accce9f38a6b91cce7f87726bcc6fd79))
* Set a default version number for each pipeline version, make version name optional ([#857](https://github.com/BLSQ/openhexa-app/issues/857)) ([168dd66](https://github.com/BLSQ/openhexa-app/commit/168dd660bd8b5c77ed0ec28093833e583dad3928))


### Bug Fixes

* **datasets:** Set the correct engine for xls files & do not crash when DatasetVersionFile do not exist anymore ([#864](https://github.com/BLSQ/openhexa-app/issues/864)) ([bb61395](https://github.com/BLSQ/openhexa-app/commit/bb6139541d872d3960967b318b38aed93f53f0a5))
* Set CMD command as json arguments ([41c6d95](https://github.com/BLSQ/openhexa-app/commit/41c6d959cfa734a8877363ae10ff8d67bcd4653b))
* silent email address trim ([#848](https://github.com/BLSQ/openhexa-app/issues/848)) ([87779c8](https://github.com/BLSQ/openhexa-app/commit/87779c8e161b83a6ad805ae3a49007c4a77216be))
* skips geometry and processes wkb ([#858](https://github.com/BLSQ/openhexa-app/issues/858)) ([eb31445](https://github.com/BLSQ/openhexa-app/commit/eb31445c1ae9095b5c73dd5f9b195789382fc6bf))

## [0.75.2](https://github.com/BLSQ/openhexa-app/compare/0.75.1...0.75.2) (2024-11-21)


### Miscellaneous Chores

* Release 0.75.2 ([81f1d84](https://github.com/BLSQ/openhexa-app/commit/81f1d8428fd090311fd67e7d06ae53a3d90bded3))

## [0.75.1](https://github.com/BLSQ/openhexa-app/compare/0.75.0...0.75.1) (2024-11-21)


### Bug Fixes

* adds byte field to json serialzer ([#851](https://github.com/BLSQ/openhexa-app/issues/851)) ([c92649e](https://github.com/BLSQ/openhexa-app/commit/c92649ec9ddf2cb32f8f146d5e8b14fe34944509))

## [0.75.0](https://github.com/BLSQ/openhexa-app/compare/0.74.7...0.75.0) (2024-11-20)


### Features

* **Pipelines:** Pipeline notifications v2 ([#846](https://github.com/BLSQ/openhexa-app/issues/846)) ([d576777](https://github.com/BLSQ/openhexa-app/commit/d576777fad0a3d1c9c267acfb50868ea2dd060e8))


### Bug Fixes

* Remove and prevent saving pipeline versions with the same name ([#849](https://github.com/BLSQ/openhexa-app/issues/849)) ([0c6c0f6](https://github.com/BLSQ/openhexa-app/commit/0c6c0f6e2cc6589a99f832cc980f60a9f2a95551))
* **settings:** In case of local hosting with a proxy, set the proxy url as the base_url as well ([68cb06a](https://github.com/BLSQ/openhexa-app/commit/68cb06a3a305a5a218af634a7bc475f1ff54fb19))

## [0.74.7](https://github.com/BLSQ/openhexa-app/compare/0.74.6...0.74.7) (2024-10-24)


### Miscellaneous Chores

* Release 0.74.7 ([3b24cca](https://github.com/BLSQ/openhexa-app/commit/3b24ccad21b3d3afd9601b078bce0ff72d4f6df0))

## [0.74.6](https://github.com/BLSQ/openhexa-app/compare/0.74.5...0.74.6) (2024-10-22)


### Bug Fixes

* fills in empty fields with NaN ([#840](https://github.com/BLSQ/openhexa-app/issues/840)) ([7ad7803](https://github.com/BLSQ/openhexa-app/commit/7ad78034ddad54f32a9baae516a66a396b6372bc))

## [0.74.5](https://github.com/BLSQ/openhexa-app/compare/0.74.4...0.74.5) (2024-10-22)


### Bug Fixes

* **CORS:** Include the files/up & files/dl to the cors exempted urls ([#835](https://github.com/BLSQ/openhexa-app/issues/835)) ([ea2d76b](https://github.com/BLSQ/openhexa-app/commit/ea2d76b26e6a08b87b70812ca746393fa7346540))

## [0.74.4](https://github.com/BLSQ/openhexa-app/compare/0.74.3...0.74.4) (2024-10-21)


### Bug Fixes

* **datasets:** move the save() in its own try..except ([43bcd1e](https://github.com/BLSQ/openhexa-app/commit/43bcd1e0553ab9f727e1acbc97a70d24f469ef39))
* **datasets:** return the dataset_file_sample to not break tests ([1da48bd](https://github.com/BLSQ/openhexa-app/commit/1da48bdd29b2d2e65df4b401c4957929a90cd1cf))
* **datasets:** When saving the sample in DB, we need a custom encoder that supports dates & uuids ([#836](https://github.com/BLSQ/openhexa-app/issues/836)) ([88c0e39](https://github.com/BLSQ/openhexa-app/commit/88c0e396062ebc0ff4833c56dc0defdee42b3029))

## [0.74.3](https://github.com/BLSQ/openhexa-app/compare/0.74.2...0.74.3) (2024-10-17)


### Bug Fixes

* **datasets:** fix the backward compatibility field 'uploadUrl' on CreateDatasetVersionFileResult ([#831](https://github.com/BLSQ/openhexa-app/issues/831)) ([a227658](https://github.com/BLSQ/openhexa-app/commit/a227658fcc607b774d57c344c669e5d1731005a8))

## [0.74.2](https://github.com/BLSQ/openhexa-app/compare/0.74.1...0.74.2) (2024-10-17)


### Bug Fixes

* CORS regex was not correct and the dev configuration was redefining unnecessary variables ([5192426](https://github.com/BLSQ/openhexa-app/commit/51924265f89ba07c3703a6bcaebdd5a9edbe59a1))
* Move removed variable from dev to the test configuration ([10894b2](https://github.com/BLSQ/openhexa-app/commit/10894b2bf69de79d6499aa10b48df73cd2983afa))
* **Pipelines:** Run outputs can be a StorageObject instance ([#830](https://github.com/BLSQ/openhexa-app/issues/830)) ([688ab7d](https://github.com/BLSQ/openhexa-app/commit/688ab7dc403b95e69e9eb009a436416b93e6d1a0))

## [0.74.1](https://github.com/BLSQ/openhexa-app/compare/0.74.0...0.74.1) (2024-10-16)


### Bug Fixes

* **cors:** CORS_URL_PREFIXES was invalid since we added the analytics ([844eef4](https://github.com/BLSQ/openhexa-app/commit/844eef462dbbce6064adf29e1bee23cdb34d214a))

## [0.74.0](https://github.com/BLSQ/openhexa-app/compare/0.73.3...0.74.0) (2024-10-09)


### Features

* **Metadata:** add generic metadata and link with dataset, version, files ([#800](https://github.com/BLSQ/openhexa-app/issues/800)) ([c1955ef](https://github.com/BLSQ/openhexa-app/commit/c1955efd076bc1404a1d44bf08269c3c8ad4b284))


### Bug Fixes

* **DB:** Starting from PostgreSQL 15+ it's needed to grant all on the public schema to allow creation and deletion of tables by the user ([#822](https://github.com/BLSQ/openhexa-app/issues/822)) ([e8b5ce2](https://github.com/BLSQ/openhexa-app/commit/e8b5ce28b4b5efde5fe634b42436af448a349f2f))

## [0.73.3](https://github.com/BLSQ/openhexa-app/compare/0.73.2...0.73.3) (2024-10-01)


### Bug Fixes

* **GCP:** Bucket cannot contain '.' or be a recognized top-level domain ([#820](https://github.com/BLSQ/openhexa-app/issues/820)) ([11da44d](https://github.com/BLSQ/openhexa-app/commit/11da44d974bebe3ed7cfecf0a1d814196aebb174))

## [0.73.2](https://github.com/BLSQ/openhexa-app/compare/0.73.1...0.73.2) (2024-10-01)


### Bug Fixes

* **GCP:** 'updated' was not passed to StorageObject for the prefixes ([b535c87](https://github.com/BLSQ/openhexa-app/commit/b535c87013bdae873d756a14273c56a1d01029d9))

## [0.73.1](https://github.com/BLSQ/openhexa-app/compare/0.73.0...0.73.1) (2024-10-01)


### Bug Fixes

* Fix wrong mgt of env var TRUST_FORWARDED_PROTO ([#816](https://github.com/BLSQ/openhexa-app/issues/816)) ([21f47b0](https://github.com/BLSQ/openhexa-app/commit/21f47b0d9711f525012524c041714620e023b574))

## [0.73.0](https://github.com/BLSQ/openhexa-app/compare/0.72.8...0.73.0) (2024-10-01)


### Features

* **Core:** add query to return password requirements ([#817](https://github.com/BLSQ/openhexa-app/issues/817)) ([8b8d5d9](https://github.com/BLSQ/openhexa-app/commit/8b8d5d90819e0154873407a9fa26d7d383c3103e))
* **Storage:** Filesystem-based storage backend for files ([d9d7159](https://github.com/BLSQ/openhexa-app/commit/d9d7159d6fc6d1982ca6f4067fb04c878dda3ceb))


### Bug Fixes

* **Dataset:** save sample as JSON instead of JSON string ([54e5214](https://github.com/BLSQ/openhexa-app/commit/54e5214eeeb323858e11a13e9dcc18833185d445))

## [0.72.8](https://github.com/BLSQ/openhexa-app/compare/0.72.7...0.72.8) (2024-09-11)


### Bug Fixes

* **Datasets:** increase slug size and only add suffix if needed ([#802](https://github.com/BLSQ/openhexa-app/issues/802)) ([93d4954](https://github.com/BLSQ/openhexa-app/commit/93d4954ddd8a10e3a6cfe4c9afd4625120b4aa5f))
* replaces dot with dash for bucket creation ([bd19d4d](https://github.com/BLSQ/openhexa-app/commit/bd19d4dcd3f3a895c2859192d0f6b8a75fa40eba))
* **Statics:** Remove cors decorator ([#809](https://github.com/BLSQ/openhexa-app/issues/809)) ([39d5ed6](https://github.com/BLSQ/openhexa-app/commit/39d5ed6cb600ee5485dedadb59c84a4d6e935358))

## 0.72.7 (2024-09-05)

**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.72.6...0.72.7

## 0.72.6 (2024-09-05)

**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.72.5...0.72.6

## 0.72.5 (2024-09-04)

**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.72.4...0.72.5

## 0.72.4 (2024-09-03)

## What's Changed
* fix(Analytics): use pipeline code for id by @cheikhgwane in https://github.com/BLSQ/openhexa-app/pull/801


**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.72.3...0.72.4

## 0.72.3 (2024-08-23)

**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.72.2...0.72.3

## 0.72.2 (2024-08-23)

## What's Changed
* Fix pipeline run user perms by @qgerome in https://github.com/BLSQ/openhexa-app/pull/795


**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.72.1...0.72.2

## 0.72.1 (2024-08-23)

## What's Changed
* Make configurable the DB hostname in the container by @toch in https://github.com/BLSQ/openhexa-app/pull/791
* fix(analytics): PipelineRunUser should be excluded by @qgerome in https://github.com/BLSQ/openhexa-app/pull/794


**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.72.0...0.72.1

## 0.72.0 (2024-08-21)

## What's Changed
* Cors pipelines webhook by @qgerome in https://github.com/BLSQ/openhexa-app/pull/762


**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.71.9...0.72.0

## 0.71.9 (2024-08-20)

**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.71.8...0.71.9

## 0.71.8 (2024-08-13)

## What's Changed
* chore: remove datasets feature flag by @cheikhgwane in https://github.com/BLSQ/openhexa-app/pull/720
* fix(Datasets): use dataset last version to track update by @cheikhgwane in https://github.com/BLSQ/openhexa-app/pull/724
* chore(deps): update dependency cachetools to v5.3.3 by @renovate in https://github.com/BLSQ/openhexa-app/pull/731
* chore(deps): update dependency croniter to v2.0.5 by @renovate in https://github.com/BLSQ/openhexa-app/pull/732
* chore(deps): update dependency google-cloud-appengine-logging to v1.4.3 by @renovate in https://github.com/BLSQ/openhexa-app/pull/739
* chore(main): release 0.71.7 by @qgerome in https://github.com/BLSQ/openhexa-app/pull/740
* chore(deps): update dependency moto to v4.2.14 by @renovate in https://github.com/BLSQ/openhexa-app/pull/745
* chore(deps): update dependency markupsafe to v2.1.5 by @renovate in https://github.com/BLSQ/openhexa-app/pull/744
* chore(deps): update dependency fiona to v1.9.6 by @renovate in https://github.com/BLSQ/openhexa-app/pull/737
* chore(deps): update dependency cryptography to v42.0.8 - autoclosed by @renovate in https://github.com/BLSQ/openhexa-app/pull/734
* chore(deps): update dependency django to v5.0.6 by @renovate in https://github.com/BLSQ/openhexa-app/pull/735
* chore(deps): update dependency grpc-google-iam-v1 to v0.13.1 by @renovate in https://github.com/BLSQ/openhexa-app/pull/742
* fix(Dev): Upgrade dockerpy to fix the pipelines runner in dev by @qgerome in https://github.com/BLSQ/openhexa-app/pull/743
* chore(deps): update actions/cache action to v4 by @renovate in https://github.com/BLSQ/openhexa-app/pull/750
* chore(deps): update docker/setup-buildx-action action to v3 by @renovate in https://github.com/BLSQ/openhexa-app/pull/755
* chore(deps): update docker/build-push-action action to v6 by @renovate in https://github.com/BLSQ/openhexa-app/pull/753
* chore(deps): update docker/login-action action to v3 by @renovate in https://github.com/BLSQ/openhexa-app/pull/754
* chore(deps): update actions/setup-python action to v5 by @renovate in https://github.com/BLSQ/openhexa-app/pull/752
* fix(Dev): pin requests version to 2.31.0 by @cheikhgwane in https://github.com/BLSQ/openhexa-app/pull/759
* chore(deps): update docker/setup-qemu-action action to v3 by @renovate in https://github.com/BLSQ/openhexa-app/pull/756
* chore(deps): update pre-commit/action action to v3.0.1 by @renovate in https://github.com/BLSQ/openhexa-app/pull/746
* chore(deps): bump certifi from 2023.11.17 to 2024.7.4 by @dependabot in https://github.com/BLSQ/openhexa-app/pull/763
* chore(deps): update reproducible-containers/buildkit-cache-dance action to v3 by @renovate in https://github.com/BLSQ/openhexa-app/pull/758
* feat : add mixpanel tracking by @cheikhgwane in https://github.com/BLSQ/openhexa-app/pull/764
* feat(Dataset): generate upload url independetly by @nazarfil in https://github.com/BLSQ/openhexa-app/pull/717
* chore(deps): update dependency django to v5.0.7 [security] by @renovate in https://github.com/BLSQ/openhexa-app/pull/767
* fix(CORS): Allow objects to be uploaded & download from everywhere by @qgerome in https://github.com/BLSQ/openhexa-app/pull/768
* chore(deps): update dependency requests to v2.32.2 [security] by @renovate in https://github.com/BLSQ/openhexa-app/pull/760
* chore(deps): update actions/checkout action to v4 by @renovate in https://github.com/BLSQ/openhexa-app/pull/751
* chore(deps): update dependency boto3 to v1.34.144 by @renovate in https://github.com/BLSQ/openhexa-app/pull/747
* chore(deps): update dependency requests to v2.32.3 by @renovate in https://github.com/BLSQ/openhexa-app/pull/769
* chore(deps): refresh pip-compile outputs by @renovate in https://github.com/BLSQ/openhexa-app/pull/748
* chore(deps): update dependency boto3 to v1.34.145 by @renovate in https://github.com/BLSQ/openhexa-app/pull/772
* chore(deps): update python docker tag to v3.12 by @renovate in https://github.com/BLSQ/openhexa-app/pull/749
* feat(Analytics): add an analytics module by @cheikhgwane in https://github.com/BLSQ/openhexa-app/pull/773
* feat(Dataset): add initial background queue, task, work and trigger t… by @nazarfil in https://github.com/BLSQ/openhexa-app/pull/719
* chore(deps): update dependency boto3 to v1.34.151 by @renovate in https://github.com/BLSQ/openhexa-app/pull/775
* chore(deps): refresh pip-compile outputs by @renovate in https://github.com/BLSQ/openhexa-app/pull/774
* feat(Databases): better count of databases tables rows by @cheikhgwane in https://github.com/BLSQ/openhexa-app/pull/777
* chore(deps): update dependency boto3 to v1.34.155 by @renovate in https://github.com/BLSQ/openhexa-app/pull/778
* chore(deps): refresh pip-compile outputs by @renovate in https://github.com/BLSQ/openhexa-app/pull/779
* chore(deps): update dependency boto3 to v1.34.156 by @renovate in https://github.com/BLSQ/openhexa-app/pull/780
* Feat background task nf by @nazarfil in https://github.com/BLSQ/openhexa-app/pull/765
* chore(deps): update dependency boto3 to v1.34.157 by @renovate in https://github.com/BLSQ/openhexa-app/pull/782
* chore(deps): update dependency boto3 to v1.34.158 by @renovate in https://github.com/BLSQ/openhexa-app/pull/783
* chore(deps): update dependency boto3 to v1.34.159 by @renovate in https://github.com/BLSQ/openhexa-app/pull/785


**Full Changelog**: https://github.com/BLSQ/openhexa-app/compare/0.71.6...0.71.8

## [0.71.7](https://github.com/BLSQ/openhexa-app/compare/0.71.6...0.71.7) (2024-06-27)


### Bug Fixes

* **Datasets:** use dataset last version to track update ([#724](https://github.com/BLSQ/openhexa-app/issues/724)) ([9550577](https://github.com/BLSQ/openhexa-app/commit/95505770bcd0f1b53fd46ec63f110a2805a75fee))


### Miscellaneous

* **deps:** update dependency cachetools to v5.3.3 ([#731](https://github.com/BLSQ/openhexa-app/issues/731)) ([b0edacc](https://github.com/BLSQ/openhexa-app/commit/b0edaccc4de1016224f0d59c034d36aa07239564))
* **deps:** update dependency croniter to v2.0.5 ([#732](https://github.com/BLSQ/openhexa-app/issues/732)) ([e08d4ad](https://github.com/BLSQ/openhexa-app/commit/e08d4ad3f94a02e7b4a68f0b617fac66d92ca92d))
* **deps:** update dependency google-cloud-appengine-logging to v1.4.3 ([#739](https://github.com/BLSQ/openhexa-app/issues/739)) ([f90ae63](https://github.com/BLSQ/openhexa-app/commit/f90ae6396eff5db1cc2e372be7bfc483b2b61c9f))
* remove datasets feature flag ([#720](https://github.com/BLSQ/openhexa-app/issues/720)) ([a6e7125](https://github.com/BLSQ/openhexa-app/commit/a6e7125d67814c04c52f281c33bbc4a43e52785b))

## [0.71.6](https://github.com/BLSQ/openhexa-app/compare/0.71.5...0.71.6) (2024-06-26)


### Bug Fixes

* Add missing migration ([b5b9da0](https://github.com/BLSQ/openhexa-app/commit/b5b9da046d438af4eadafa31c2e53525bced5b48))
* **Pipelines:** Returns the secret value of the connection fields when in a pipeline environment ([4de283f](https://github.com/BLSQ/openhexa-app/commit/4de283f0d3c877def3165cc85c237fd7c1f56f02))


### Miscellaneous

* add blank=True on PipelineRun.duration & .stopped_by ([350238e](https://github.com/BLSQ/openhexa-app/commit/350238e70ab64476342a4860dcfffefaaf07cfa2))
* Add renovate.json ([#729](https://github.com/BLSQ/openhexa-app/issues/729)) ([3e6f859](https://github.com/BLSQ/openhexa-app/commit/3e6f85951f9ed865e7c692b91bc2b5c816268c20))
* **CI:** Add a concurrenty rule to avoid having multiple release-please runs at the same time ([24d9966](https://github.com/BLSQ/openhexa-app/commit/24d996669532d825894092f830be89f74ae37fb3))
* Delete .github/dependabot.yml ([9cd4f9d](https://github.com/BLSQ/openhexa-app/commit/9cd4f9d2146ea8a9fa0f7d8bdba68285d4dd1c2b))
* **deps:** bump urllib3 from 1.26.18 to 1.26.19 ([#718](https://github.com/BLSQ/openhexa-app/issues/718)) ([c21229e](https://github.com/BLSQ/openhexa-app/commit/c21229e3ff28e42ada4e1f99caf098eb90b6bf09))

## [0.71.5](https://github.com/BLSQ/openhexa-app/compare/0.71.4...0.71.5) (2024-06-25)


### Bug Fixes

* **Connections:** specify connection workspace ([#727](https://github.com/BLSQ/openhexa-app/issues/727)) ([d1889dd](https://github.com/BLSQ/openhexa-app/commit/d1889dddc3ca1dfd2f4a192118daa0bacbeca4a1))

## [0.71.4](https://github.com/BLSQ/openhexa-app/compare/0.71.3...0.71.4) (2024-06-25)


### Bug Fixes

* **Pipelines:** handle case of notebook pipeline ([#721](https://github.com/BLSQ/openhexa-app/issues/721)) ([9575292](https://github.com/BLSQ/openhexa-app/commit/957529238f528e7e805f3d8498cd2f7defd8fd6a))

## [0.71.3](https://github.com/BLSQ/openhexa-app/compare/0.71.2...0.71.3) (2024-06-25)


### Bug Fixes

* **pipelines:** Fix scheduler of pipelines ([fa9ec87](https://github.com/BLSQ/openhexa-app/commit/fa9ec876a794461c408fccc4dac65f6c366e6376))

## [0.71.2](https://github.com/BLSQ/openhexa-app/compare/0.71.1...0.71.2) (2024-06-24)


### Bug Fixes

* **Connections:** remove wrong 'archived' in the criteria ([1afedb3](https://github.com/BLSQ/openhexa-app/commit/1afedb3591179b6d1570c8ac9abc8a51c80dd125))

## [0.71.1](https://github.com/BLSQ/openhexa-app/compare/0.71.0...0.71.1) (2024-06-24)


### Bug Fixes

* **Connections:** filter_for_user should be callable by a pipeline ([ce7d2fa](https://github.com/BLSQ/openhexa-app/commit/ce7d2fa9f4a885da1ca5dabc1325b64f6750797c))

## [0.71.0](https://github.com/BLSQ/openhexa-app/compare/0.70.1...0.71.0) (2024-06-18)


### Features

* **Pipelines:** add authentication to wehbook ([#714](https://github.com/BLSQ/openhexa-app/issues/714)) ([2a6b3ce](https://github.com/BLSQ/openhexa-app/commit/2a6b3ce45e543a9b005cda642d9668958b1dfa33))
* **pipelines:** Configuration on pipeline's version ([acfa76b](https://github.com/BLSQ/openhexa-app/commit/acfa76bfb78d4e89f7823c5fa3b686e1160e5d19))
* **Workspaces:** retrieve workspace connection by slug ([#711](https://github.com/BLSQ/openhexa-app/issues/711)) ([9617063](https://github.com/BLSQ/openhexa-app/commit/96170637fb8e1450bc6e42257ec80ee6b81c63af))


### Miscellaneous

* **Connections:** stop injecting connections creds in env var ([#715](https://github.com/BLSQ/openhexa-app/issues/715)) ([217f2c1](https://github.com/BLSQ/openhexa-app/commit/217f2c1212360a8f1e0cd65321bd85b35c4a6c31))
* **GraphQL:** Update documentation of graphql files ([#712](https://github.com/BLSQ/openhexa-app/issues/712)) ([2be6c87](https://github.com/BLSQ/openhexa-app/commit/2be6c87961b7838c3170050be9db1ab693e92140))
* Update database port in docker-compose.yaml ([#709](https://github.com/BLSQ/openhexa-app/issues/709)) ([1a5378b](https://github.com/BLSQ/openhexa-app/commit/1a5378b61320801babe5eb6d29c08872612ee4f1))

## [0.70.1](https://github.com/BLSQ/openhexa-app/compare/0.70.0...0.70.1) (2024-05-27)


### Features

* **Connections:** editor can create/update/delete connection ([#706](https://github.com/BLSQ/openhexa-app/issues/706)) ([2b6d432](https://github.com/BLSQ/openhexa-app/commit/2b6d432a653824dab72a5e7564c2c7412db2358f))


### Miscellaneous

* Release 0.70.1 ([5448a4c](https://github.com/BLSQ/openhexa-app/commit/5448a4c774070e7367b05c6a0ff194a7996da3ae))

## [0.70.0](https://github.com/BLSQ/openhexa-app/compare/0.69.3...0.70.0) (2024-05-17)


### Features

* **Pipelines:** create pipeline from notebook ([3cac4d7](https://github.com/BLSQ/openhexa-app/commit/3cac4d769369703d6abaf1f5dc0d93c93897ad6e))
* **Pipelines:** validate parameter types upon PipelineVersion run ([#699](https://github.com/BLSQ/openhexa-app/issues/699)) ([fa89e59](https://github.com/BLSQ/openhexa-app/commit/fa89e59194d8f766c181f4de3e4347058d1f7894))
* **Workspaces:** add feature flag to allow users the creation of workspaces ([121a53a](https://github.com/BLSQ/openhexa-app/commit/121a53a14515ad46bb881532561b243918d1fdcd))
* **Workspaces:** allow user to update workspace image and rename PIPELINE_IMAGE env ([#700](https://github.com/BLSQ/openhexa-app/issues/700)) ([2ced1cb](https://github.com/BLSQ/openhexa-app/commit/2ced1cb42a93070005bbc2bf318e3635fff54287))


### Miscellaneous

* **dev:** Add a frontend profile to run the frontend from the app repo ([#702](https://github.com/BLSQ/openhexa-app/issues/702)) ([e16a844](https://github.com/BLSQ/openhexa-app/commit/e16a844fc0cee64b32a09874eeaf1305536e7f2e))

## [0.69.3](https://github.com/BLSQ/openhexa-app/compare/0.69.2...0.69.3) (2024-05-08)


### Bug Fixes

* **Buckets:** Fix the way we set the labels on the gcp bucket ([97ea340](https://github.com/BLSQ/openhexa-app/commit/97ea340cc111232a4e40ff0e47c5784f5a6cdfea))

## [0.69.2](https://github.com/BLSQ/openhexa-app/compare/0.69.1...0.69.2) (2024-04-30)


### Bug Fixes

* **Pipelines:** Fix the way we set the duration inside the translate block ([#692](https://github.com/BLSQ/openhexa-app/issues/692)) ([84fe452](https://github.com/BLSQ/openhexa-app/commit/84fe452835e06bbb6b3bf4093b173285064aeff9))


### Miscellaneous

* **GCP:** Set the workspace as a label on the bucket of the workspacee ([#689](https://github.com/BLSQ/openhexa-app/issues/689)) ([366c7a1](https://github.com/BLSQ/openhexa-app/commit/366c7a19a4d839bba86c71b82b03f4efcb063627))

## [0.69.1](https://github.com/BLSQ/openhexa-app/compare/0.69.0...0.69.1) (2024-04-18)


### Bug Fixes

* **CI:** Use the registry to cache the layers ([2d40ba0](https://github.com/BLSQ/openhexa-app/commit/2d40ba0f29498ab2e06649aeccc3786dc5bc5de4))
* **Pipelines:** enable nulls value check on Pipeline model constraint ([#685](https://github.com/BLSQ/openhexa-app/issues/685)) ([c98b789](https://github.com/BLSQ/openhexa-app/commit/c98b78994c94d4d0efa7fc0fdc52390b48d1e690))


### Miscellaneous

* **Admin:** Add inlines and better search filters to various models ([#683](https://github.com/BLSQ/openhexa-app/issues/683)) ([191a3ce](https://github.com/BLSQ/openhexa-app/commit/191a3ce4c690378487283174d075d33402bac2e3))
* **Billing:** Add a label on the pipelines pod with the workspace ([a58bfae](https://github.com/BLSQ/openhexa-app/commit/a58bfaeda837dc06d3773a020e787190fa7624b0))
* **deps:** bump gunicorn from 21.2.0 to 22.0.0 ([#686](https://github.com/BLSQ/openhexa-app/issues/686)) ([3a2d3f1](https://github.com/BLSQ/openhexa-app/commit/3a2d3f1c01598b79576442827d44bc8a28d92def))
* **deps:** bump sqlparse from 0.4.4 to 0.5.0 ([#684](https://github.com/BLSQ/openhexa-app/issues/684)) ([3bba33b](https://github.com/BLSQ/openhexa-app/commit/3bba33b9318c4976d512243a890dc87ce366c813))

## [0.69.0](https://github.com/BLSQ/openhexa-app/compare/0.68.2...0.69.0) (2024-04-15)


### Features

* **pipelines:** Add permissions on PipelineVersion; users can update versions ([#680](https://github.com/BLSQ/openhexa-app/issues/680)) ([9557396](https://github.com/BLSQ/openhexa-app/commit/95573960549bddff8a8cd53579c8260f2c97e46d))


### Miscellaneous

* **Debt:** Remove all HTML pages handled by the frontend, remove the ui templates; removing deprecated graphql ([#678](https://github.com/BLSQ/openhexa-app/issues/678)) ([af576bc](https://github.com/BLSQ/openhexa-app/commit/af576bc66d98b8872ae9410d110548261b478e0a))

## [0.68.2](https://github.com/BLSQ/openhexa-app/compare/0.68.1...0.68.2) (2024-04-10)


### Bug Fixes

* **pipelines:** Add a new resolver pipelineVersion for the return of uploadPipeline ([3321900](https://github.com/BLSQ/openhexa-app/commit/33219005fea5dedefcf253a24994f87a7f9e1b07))

## [0.68.1](https://github.com/BLSQ/openhexa-app/compare/0.68.0...0.68.1) (2024-04-08)


### Bug Fixes

* Put back wait-for-it in docker-entrypoint ([00071d5](https://github.com/BLSQ/openhexa-app/commit/00071d5107f284dc777201a4bc12d9cca927fa86))
* **SoftDelete:** hard delete model on django admin ([#676](https://github.com/BLSQ/openhexa-app/issues/676)) ([bd6b322](https://github.com/BLSQ/openhexa-app/commit/bd6b3229953226bb095192c5cc74f03372a23ea3))

## [0.68.0](https://github.com/BLSQ/openhexa-app/compare/0.67.0...0.68.0) (2024-04-05)


### Features

* **Pipelines:** Add a name, description and link to the version model ([#672](https://github.com/BLSQ/openhexa-app/issues/672)) ([7a680d6](https://github.com/BLSQ/openhexa-app/commit/7a680d60fbee67f95f2a357c83041ecac19ea06b))
* **Pipelines:** allow user to stop a pipeline ([#670](https://github.com/BLSQ/openhexa-app/issues/670)) ([75f005e](https://github.com/BLSQ/openhexa-app/commit/75f005e8285c6838b1ee33d1864e92de4804a718))


### Bug Fixes

* **tests:** Remove collation from the latter migration file, merge migrations ([de8a520](https://github.com/BLSQ/openhexa-app/commit/de8a52037d3fdd3eb11cc81e276bf113d5129c27))


### Miscellaneous

* **DB:** Add case_insensitive collation to the first migration ([259ecc9](https://github.com/BLSQ/openhexa-app/commit/259ecc95f4ae7e05c15f60301c9c22b316561dfb))

## [0.67.0](https://github.com/BLSQ/openhexa-app/compare/0.66.5...0.67.0) (2024-03-26)


### Features

* **Pipelines:** enable soft delete of pipeline ([#663](https://github.com/BLSQ/openhexa-app/issues/663)) ([5511e50](https://github.com/BLSQ/openhexa-app/commit/5511e5098a4fba8a79423d40c00fce22de39bd92))


### Bug Fixes

* **datasets:** Allow pipelines to download linked datasets ([#671](https://github.com/BLSQ/openhexa-app/issues/671)) ([019e4ba](https://github.com/BLSQ/openhexa-app/commit/019e4baa80f40117af553ce1ed42ea98f62be601))
* **Files:** Do not log missing output files in Sentry ([#669](https://github.com/BLSQ/openhexa-app/issues/669)) ([f526543](https://github.com/BLSQ/openhexa-app/commit/f52654360a706574ec5e757f9fc42c0b38b26334))


### Miscellaneous

* **deps:** bump cryptography from 42.0.2 to 42.0.4 ([#664](https://github.com/BLSQ/openhexa-app/issues/664)) ([e090914](https://github.com/BLSQ/openhexa-app/commit/e0909140c81947467425ff0e3b8744877969df5a))
* **deps:** bump django from 5.0.2 to 5.0.3 ([#668](https://github.com/BLSQ/openhexa-app/issues/668)) ([48fb9e0](https://github.com/BLSQ/openhexa-app/commit/48fb9e02323fa020b4c2f1b384037ac9d82bac90))

## [0.66.5](https://github.com/BLSQ/openhexa-app/compare/0.66.4...0.66.5) (2024-03-05)


### Bug Fixes

* **Pipelines:** typo on permission module ([#665](https://github.com/BLSQ/openhexa-app/issues/665)) ([30e7e7e](https://github.com/BLSQ/openhexa-app/commit/30e7e7e2956a0208a47fffaf2bf4d27a0ab38968))
* **S3:** Catch the exception and log it to sentry ([8531e94](https://github.com/BLSQ/openhexa-app/commit/8531e94ed2b5b579a14c7cb1a4c48de48154c7a3))

## [0.66.4](https://github.com/BLSQ/openhexa-app/compare/0.66.3...0.66.4) (2024-02-21)


### Miscellaneous

* **deps:** bump cryptography from 42.0.0 to 42.0.2 ([#657](https://github.com/BLSQ/openhexa-app/issues/657)) ([5f9b487](https://github.com/BLSQ/openhexa-app/commit/5f9b487d6223d733e078f85b6cd4d7d042ab2c91))
* remove old comment in dockerfile ([a30d389](https://github.com/BLSQ/openhexa-app/commit/a30d389d9ac587e307b1a350a5094592433fc65f))

## [0.66.3](https://github.com/BLSQ/openhexa-app/compare/0.66.2...0.66.3) (2024-02-20)


### Bug Fixes

* **Dockerfile:** Add caching ([9280a7e](https://github.com/BLSQ/openhexa-app/commit/9280a7ec7aea17b555f00e5a136a711ffa286cb1))


### Miscellaneous

* Use gha cache instead of the registry ([a8775e9](https://github.com/BLSQ/openhexa-app/commit/a8775e93a580dd51eb3dddba88aa6f2f50678b24))

## [0.66.2](https://github.com/BLSQ/openhexa-app/compare/0.66.1...0.66.2) (2024-02-20)


### Bug Fixes

* **Image:** Install procps to have pkill ([4f251ec](https://github.com/BLSQ/openhexa-app/commit/4f251ecfab847d22185ef09cb08eafce3c94fd66))

## [0.66.1](https://github.com/BLSQ/openhexa-app/compare/0.66.0...0.66.1) (2024-02-20)


### Bug Fixes

* **Config:** Do not use double quotes in formatted strings ([c99fa90](https://github.com/BLSQ/openhexa-app/commit/c99fa9054660b3a340d8e74741c6afc3b3daf6f1))
* **Docker:** Wrong python version used with dockerfile ([6b516be](https://github.com/BLSQ/openhexa-app/commit/6b516bedbf79172e0e893bcd0ddaad3388eef5cf))


### Miscellaneous

* **Fixtures:** Add base fixtures that will always be loaded in the database on deployment ([b04a587](https://github.com/BLSQ/openhexa-app/commit/b04a587de9c8df148afbbd33e44d706e75af9255))

## [0.66.0](https://github.com/BLSQ/openhexa-app/compare/0.65.2...0.66.0) (2024-02-19)


### Features

* S3 custom client endpoint ([#646](https://github.com/BLSQ/openhexa-app/issues/646)) ([429d46b](https://github.com/BLSQ/openhexa-app/commit/429d46b1f3962dee19e9c2818c811ae577d405b7))


### Bug Fixes

* **GCP:** Enable bucket versioning for future buckets & add a lifecycle policy ([#654](https://github.com/BLSQ/openhexa-app/issues/654)) ([8a9bfb8](https://github.com/BLSQ/openhexa-app/commit/8a9bfb8e86b82c4b48965e2476f6ba0e4fdb600f))
* **PipelineRun:** change NotFound exception import ([#652](https://github.com/BLSQ/openhexa-app/issues/652)) ([b367fe0](https://github.com/BLSQ/openhexa-app/commit/b367fe0f6426a25ad4da6a75580ce784e0ff39bd))
* **Settings:** Take SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, SECURE_SSL_REDIRECT from os.environ ([ac1ccb0](https://github.com/BLSQ/openhexa-app/commit/ac1ccb013845aea866002cdcf04e7bfc03bc6570))


### Miscellaneous

* Add isLatestVersion on PipelineVersion ([#651](https://github.com/BLSQ/openhexa-app/issues/651)) ([21a881c](https://github.com/BLSQ/openhexa-app/commit/21a881c02e1db17461458492aa177fcf3d85a545))
* **Debt:** Remove comments app models and templates (first step) ([#649](https://github.com/BLSQ/openhexa-app/issues/649)) ([f8fb49f](https://github.com/BLSQ/openhexa-app/commit/f8fb49fdef2ca445e4a94ee3dba3ad0ceba36d6b))
* **Debt:** Start to remove the comments app ([d370863](https://github.com/BLSQ/openhexa-app/commit/d370863b762e0fd0a9ba23ac2d9e33ce0314e688))
* **deps:** bump cryptography from 41.0.7 to 42.0.0 ([#642](https://github.com/BLSQ/openhexa-app/issues/642)) ([1f8370e](https://github.com/BLSQ/openhexa-app/commit/1f8370eb06ff898f538b40a1d0b73bfb536f4e87))
* **deps:** bump django from 5.0 to 5.0.2 ([#648](https://github.com/BLSQ/openhexa-app/issues/648)) ([a64b969](https://github.com/BLSQ/openhexa-app/commit/a64b969bde883e27ae60e50df297e6a222d8646a))
* **deps:** bump starlette from 0.34.0 to 0.36.2 ([#641](https://github.com/BLSQ/openhexa-app/issues/641)) ([fcfe3e8](https://github.com/BLSQ/openhexa-app/commit/fcfe3e8f24f69729344a6b6b00d61cdf9d716d6c))
* **Pipelines:** Remove the temporary status page ([#653](https://github.com/BLSQ/openhexa-app/issues/653)) ([57fd504](https://github.com/BLSQ/openhexa-app/commit/57fd5049f9b74fad01c02c51c4f57fc619c97016))
* Set the default storage engine to GCP ([f81247d](https://github.com/BLSQ/openhexa-app/commit/f81247d2f019ef3b57a83cf6286c7650cb4fa78c))

## [0.65.2](https://github.com/BLSQ/openhexa-app/compare/0.65.1...0.65.2) (2024-02-07)


### Features

* **Storage:** Workspace buckets can be configured to work on GCP or S3 ([3b3b400](https://github.com/BLSQ/openhexa-app/commit/3b3b400ef681d6cfe2d9f872eb6e4a59ec22ae8c))
* **Workspaces:** do not add existing users to workspace by default ([#640](https://github.com/BLSQ/openhexa-app/issues/640)) ([d56de58](https://github.com/BLSQ/openhexa-app/commit/d56de5876d071ec59cd28a54ddac4123f421dfe5))


### Miscellaneous

* release 0.65.2 ([ddff7b3](https://github.com/BLSQ/openhexa-app/commit/ddff7b3bd2770eec0d1070182286d1c136031ced))

## [0.65.1](https://github.com/BLSQ/openhexa-app/compare/0.65.0...0.65.1) (2024-02-06)


### Bug Fixes

* **Notebooks:** Logout the user from jupyterhub on logout ([#636](https://github.com/BLSQ/openhexa-app/issues/636)) ([053ebde](https://github.com/BLSQ/openhexa-app/commit/053ebde246626cfe984daa00d050b89701f75154))
* **Schema:** Add a BigInt type to the schema ([#643](https://github.com/BLSQ/openhexa-app/issues/643)) ([d8b5e25](https://github.com/BLSQ/openhexa-app/commit/d8b5e25c0893196f75ba13e53ae5ae235aefe6eb))


### Miscellaneous

* **Docker:** Add image config to docker-compose.yaml ([0e47516](https://github.com/BLSQ/openhexa-app/commit/0e4751693fd3092b77bdf5112ba741ea3aa757b4))

## [0.65.0](https://github.com/BLSQ/openhexa-app/compare/0.64.2...0.65.0) (2024-01-29)


### Features

* **Datasets:** link datasetVersion to pipelinRun ([#631](https://github.com/BLSQ/openhexa-app/issues/631)) ([db68a7a](https://github.com/BLSQ/openhexa-app/commit/db68a7abcfda30c6d6092ac260b1abd0dd61d163))


### Bug Fixes

* **Auth:** Only tokens from running pipelines can be used to authenticate the user ([#635](https://github.com/BLSQ/openhexa-app/issues/635)) ([399ffa2](https://github.com/BLSQ/openhexa-app/commit/399ffa28de85198dd53bd2b7b2524fed8f82de3a))
* **PipelineRun:** check if table/file_path exist ([#634](https://github.com/BLSQ/openhexa-app/issues/634)) ([863d925](https://github.com/BLSQ/openhexa-app/commit/863d9250b58868fc0774205b4d5827d277b7b6fb))
* **Pipelines:** fix tests ([#637](https://github.com/BLSQ/openhexa-app/issues/637)) ([997ceba](https://github.com/BLSQ/openhexa-app/commit/997ceba9ec30405dbbcfa4aa7079cc774845c83a))
* **Pipelines:** It the db cannot be reached do not append None to outputs ([58ee429](https://github.com/BLSQ/openhexa-app/commit/58ee42956ecaa47a4909b6d5651b091153dd4398))


### Miscellaneous

* **i18n:** Update translations ([2eb3cb7](https://github.com/BLSQ/openhexa-app/commit/2eb3cb740a9ef12d47c012f9d7eb9fc555bafaec))
* **Metrics:** deleting metrics app ([#630](https://github.com/BLSQ/openhexa-app/issues/630)) ([41eed63](https://github.com/BLSQ/openhexa-app/commit/41eed63c93289677ebdf630d62f2690b72f2ed56))

## [0.64.2](https://github.com/BLSQ/openhexa-app/compare/0.64.1...0.64.2) (2024-01-18)


### Bug Fixes

* **settings:** Set the new docker image for the pipeline & by default use the pipeline image for the workspace as well ([2ded8d0](https://github.com/BLSQ/openhexa-app/commit/2ded8d08975c6241dd23ccb020ec83b917e174b7))

## [0.64.1](https://github.com/BLSQ/openhexa-app/compare/0.64.0...0.64.1) (2024-01-16)


### Miscellaneous

* **deps:** bump jinja2 from 3.1.2 to 3.1.3 ([#628](https://github.com/BLSQ/openhexa-app/issues/628)) ([036052b](https://github.com/BLSQ/openhexa-app/commit/036052b59f9f7163fb27806c7f2ea0584768cf48))
* remove metrics ([#629](https://github.com/BLSQ/openhexa-app/issues/629)) ([7840d0d](https://github.com/BLSQ/openhexa-app/commit/7840d0dfe9c526a7cb4ae8a80ff64264a20b5d49))
* Set container_name for the app ([54d6c8f](https://github.com/BLSQ/openhexa-app/commit/54d6c8f96451352168d494e783c78a37ecc9e0b6))

## [0.64.0](https://github.com/BLSQ/openhexa-app/compare/0.63.2...0.64.0) (2024-01-08)


### Features

* **Files:** Filter files matching a substring ([a119ea9](https://github.com/BLSQ/openhexa-app/commit/a119ea9daaf10fd2eeb9c97e0afaba4f623cd806))
* **Files:** Filter files matching a substring ([#621](https://github.com/BLSQ/openhexa-app/issues/621)) ([06d3321](https://github.com/BLSQ/openhexa-app/commit/06d3321d882b58074924b402a09cc0957f20dcb0))
* **i18n:** App is translatable ([#624](https://github.com/BLSQ/openhexa-app/issues/624)) ([c19e7fb](https://github.com/BLSQ/openhexa-app/commit/c19e7fb8de1d15323499c51dd87b3456f0c948c0))
* User can register & see their workspace's invitations ([#613](https://github.com/BLSQ/openhexa-app/issues/613)) ([81ec731](https://github.com/BLSQ/openhexa-app/commit/81ec731b2fedd8ed8c30fccc74751fd1ccfeec82))


### Bug Fixes

* **tests:** Missing openHexa ([799bb55](https://github.com/BLSQ/openhexa-app/commit/799bb559768b7a1b2b9177abc5f3775ed884e32b))

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

- Added the foundations of the OpenHEXA GraphQL API
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
