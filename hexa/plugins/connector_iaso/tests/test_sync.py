import unittest.mock

from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.test import TestCase
from hexa.plugins.connector_iaso.models import IASOAccount


class SyncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.iaso_account = IASOAccount.objects.create(name="iaso-dev")

    def test_empty_sync(self):
        self.assertEqual(self.iaso_account.iasoform_set.count(), 0)
        self.assertEqual(self.iaso_account.iasoorgunit_set.count(), 0)
        with unittest.mock.patch.multiple(
            "hexa.plugins.connector_iaso.models",
            get_forms_json=unittest.mock.DEFAULT,
            get_orgunits_level12=unittest.mock.DEFAULT,
        ) as mocks:
            mocks["get_forms_json"].return_value = []
            mocks["get_orgunits_level12"].return_value = []
            self.iaso_account.sync()
        self.assertQuerysetEqual(self.iaso_account.iasoform_set.all(), [])
        self.assertQuerysetEqual(self.iaso_account.iasoorgunit_set.all(), [])

    def test_sync_base(self):
        with unittest.mock.patch.multiple(
            "hexa.plugins.connector_iaso.models",
            get_forms_json=unittest.mock.DEFAULT,
            get_orgunits_level12=unittest.mock.DEFAULT,
        ) as mocks:
            mocks["get_orgunits_level12"].return_value = []
            mocks["get_forms_json"].return_value = [
                {
                    "id": 2,
                    "name": "Questionnaire 1",
                    "form_id": "A_Data_Q1",
                    "org_unit_types": [
                        {
                            "id": 9,
                            "name": "Province",
                            "short_name": "Prov",
                            "created_at": 1561062550.970094,
                            "updated_at": 1652194635.461252,
                            "depth": 1,
                        }
                    ],
                    "org_unit_type_ids": [9],
                    "projects": [
                        {
                            "id": 1,
                            "name": "BLSQTEST",
                            "app_id": "org.bluesquarehub.iaso",
                        },
                        {
                            "id": 10,
                            "name": "Demo project",
                            "app_id": "com.bluesquarehub.iaso",
                        },
                    ],
                    "project_ids": [1, 10],
                    "latest_form_version": {
                        "id": 6,
                        "version_id": "2",
                        "file": "https://iaso-stg.local/forms/Questionaire_1.xml",
                        "created_at": 1576686655.95713,
                        "updated_at": 1576686655.957162,
                    },
                    "created_at": 1561387479.124504,
                    "updated_at": 1631134368.64165,
                },
                {
                    "id": 7,
                    "name": "Questionnaire 2",
                    "form_id": "A_Data_Q2",
                    "device_field": "",
                    "location_field": "ssc_107.1",
                    "org_unit_types": [
                        {
                            "id": 12,
                            "name": "Site de santé communautaire",
                            "short_name": "SSC",
                            "created_at": 1561062551.004035,
                            "updated_at": 1569425808.955913,
                        }
                    ],
                    "org_unit_type_ids": [12],
                    "projects": [
                        {
                            "id": 1,
                            "name": "BLSQTEST",
                            "app_id": "org.bluesquarehub.iaso",
                        },
                        {
                            "id": 10,
                            "name": "Demo project",
                            "app_id": "com.bluesquarehub.iaso",
                        },
                    ],
                    "project_ids": [1, 10],
                    "latest_form_version": {},
                    "created_at": 1561387688.985039,
                    "updated_at": 1631134368.644889,
                },
            ]
            sync_result = self.iaso_account.sync()
            self.assertEqual(self.iaso_account.iasoorgunit_set.count(), 0)
            self.assertEqual(self.iaso_account.iasoform_set.count(), 2)
            self.assertEqual(sync_result.created, 2)

            # Sync again, should not differ
            sync_result = self.iaso_account.sync()
            self.assertEqual(self.iaso_account.iasoorgunit_set.count(), 0)
            self.assertEqual(self.iaso_account.iasoform_set.count(), 2)
            self.assertEqual(sync_result.identical, 2)

    def test_sync_remove_add(self):
        with unittest.mock.patch.multiple(
            "hexa.plugins.connector_iaso.models",
            get_forms_json=unittest.mock.DEFAULT,
            get_orgunits_level12=unittest.mock.DEFAULT,
        ) as mocks:
            mocks["get_orgunits_level12"].return_value = []
            mocks["get_forms_json"].return_value = [
                {
                    "id": 2,
                    "name": "Questionnaire 1",
                    "form_id": "A_Data_Q1",
                    "org_unit_types": [],
                    "org_unit_type_ids": [],
                    "projects": [],
                    "project_ids": [],
                    "latest_form_version": {},
                    "created_at": 1561387479.124504,
                    "updated_at": 1631134368.64165,
                },
                {
                    "id": 7,
                    "name": "Questionnaire 2",
                    "form_id": "A_Data_Q2",
                    "org_unit_types": [],
                    "org_unit_type_ids": [],
                    "projects": [],
                    "project_ids": [],
                    "latest_form_version": {},
                    "created_at": 1561387688.985039,
                    "updated_at": 1631134368.644889,
                },
                {
                    "id": 8,
                    "name": "Questionnaire 3",
                    "form_id": "A_Data_Q3",
                    "org_unit_types": [],
                    "org_unit_type_ids": [],
                    "projects": [],
                    "project_ids": [],
                    "latest_form_version": {},
                    "created_at": 1588387699.123456,
                    "updated_at": 1678910234.789101,
                },
            ]

            # Sync a first time
            sync_result = self.iaso_account.sync()
            self.assertEqual(
                DatasourceSyncResult(datasource=self.iaso_account, created=3),
                sync_result,
            )

            # Delete id2, add id18 & id20
            mocks["get_forms_json"].return_value = [
                {
                    "id": 7,
                    "name": "Questionnaire 2",
                    "form_id": "A_Data_Q2",
                    "org_unit_types": [],
                    "org_unit_type_ids": [],
                    "projects": [],
                    "project_ids": [],
                    "latest_form_version": {},
                    "created_at": 1561387688.985039,
                    "updated_at": 1631134368.644889,
                },
                {
                    "id": 8,
                    "name": "Questionnaire 3",
                    "form_id": "A_Data_Q3",
                    "org_unit_types": [],
                    "org_unit_type_ids": [],
                    "projects": [],
                    "project_ids": [],
                    "latest_form_version": {},
                    "created_at": 1588387699.123456,
                    "updated_at": 1678910234.789101,
                },
                {
                    "id": 18,
                    "name": "Questionnaire 4",
                    "form_id": "A_Data_Q4",
                    "org_unit_types": [],
                    "org_unit_type_ids": [],
                    "projects": [],
                    "project_ids": [],
                    "latest_form_version": {},
                    "created_at": 1588387699.123456,
                    "updated_at": 1678910234.789101,
                },
                {
                    "id": 20,
                    "name": "Questionnaire 5",
                    "form_id": "A_Data_Q5",
                    "org_unit_types": [],
                    "org_unit_type_ids": [],
                    "projects": [],
                    "project_ids": [],
                    "latest_form_version": {},
                    "created_at": 1588387699.123456,
                    "updated_at": 1678910234.789101,
                },
            ]

            # Sync again
            sync_result = self.iaso_account.sync()
            self.assertEqual(
                DatasourceSyncResult(
                    datasource=self.iaso_account, created=2, identical=2, deleted=1
                ),
                sync_result,
            )
