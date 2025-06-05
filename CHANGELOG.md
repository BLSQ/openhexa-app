# Changelog

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
