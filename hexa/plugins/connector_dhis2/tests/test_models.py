from datetime import timedelta
from logging import getLogger
from unittest.mock import patch

import responses
from django.utils import timezone

from hexa.catalog.models import Index
from hexa.core.test import TestCase
from hexa.plugins.connector_dhis2.api import DataElementResult, Dhis2Client
from hexa.plugins.connector_dhis2.models import (
    Credentials,
    DataElement,
    DataSet,
    Indicator,
    IndicatorType,
    Instance,
    InstancePermission,
    OrganisationUnit,
)
from hexa.plugins.connector_dhis2.sync import sync_from_dhis2_results
from hexa.user_management.models import Membership, Team, User

from .mock_data import (
    mock_data_elements_response,
    mock_datasets_response,
    mock_indicator_types_response,
    mock_indicators_response,
    mock_info_json,
    mock_orgunits_response,
)

logger = getLogger(__name__)


class ModelsTestTest(TestCase):
    DHIS2_INSTANCE_PLAY = None
    DATA_ELEMENT_FOO = None
    INDICATOR_BAR = None
    USER_BJORN = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_BJORN = User.objects.create_user(
            "bjorn@bluesquarehub.com",
            "bjornbjorn",
        )
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            url="https://play.dhis2.org.invalid",
        )
        cls.DATA_ELEMENT_FOO = DataElement.objects.create(
            name="Foo",
            external_access=False,
            favorite=False,
            created=timezone.now(),
            last_updated=timezone.now(),
            instance=cls.DHIS2_INSTANCE_PLAY,
        )
        cls.INDICATOR_BAR = Indicator.objects.create(
            name="Bar",
            external_access=False,
            favorite=False,
            annualized=False,
            created=timezone.now(),
            last_updated=timezone.now(),
            instance=cls.DHIS2_INSTANCE_PLAY,
        )

    def test_delete_data_element(self):
        """Deleting a data element should delete its index as well"""
        data_element = DataElement.objects.create(
            name="some-data-element",
            external_access=False,
            favorite=False,
            created=timezone.now(),
            last_updated=timezone.now(),
            instance=self.DHIS2_INSTANCE_PLAY,
        )
        data_element_id = data_element.id
        self.assertEqual(1, Index.objects.filter(object_id=data_element_id).count())
        data_element.delete()
        self.assertEqual(0, Index.objects.filter(object_id=data_element_id).count())


class PermissionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DHIS2A = Instance.objects.create(
            url="https://play1.dhis2.org.invalid", slug="invalidA"
        )
        cls.DHIS2B = Instance.objects.create(
            url="https://play2.dhis2.org.invalid", slug="invalidB"
        )
        cls.TEAM1 = Team.objects.create(name="Test Team1")
        cls.TEAM2 = Team.objects.create(name="Test Team2")
        InstancePermission.objects.create(instance=cls.DHIS2A, team=cls.TEAM1)
        InstancePermission.objects.create(instance=cls.DHIS2A, team=cls.TEAM2)
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
        )
        Membership.objects.create(team=cls.TEAM1, user=cls.USER_REGULAR)
        Membership.objects.create(team=cls.TEAM2, user=cls.USER_REGULAR)
        cls.USER_SUPER = User.objects.create_user(
            "mary@bluesquarehub.com",
            "super",
            is_superuser=True,
        )

    def test_instance_dedup(self):
        """
        - user super see 2 instances (all of them)
        - user regular see only test instance 1, one time
        """
        self.assertEqual(
            list(
                Instance.objects.filter_for_user(self.USER_REGULAR)
                .order_by("url")
                .values("url")
            ),
            [{"url": "https://play1.dhis2.org.invalid"}],
        )
        self.assertEqual(
            list(
                Instance.objects.filter_for_user(self.USER_SUPER)
                .order_by("url")
                .values("url")
            ),
            [
                {"url": "https://play1.dhis2.org.invalid"},
                {"url": "https://play2.dhis2.org.invalid"},
            ],
        )


class DHIS2SyncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            url="https://play.dhis2.org.invalid",
            api_credentials=Credentials.objects.create(
                api_url="https://play.dhis2.org.invalid",
                username="test_username",
                password="test_password",
            ),
            verbose_sync=True,
        )

    @responses.activate
    def test_sync(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/api/system/info.json",
            json=mock_info_json,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/api/dataElements.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_data_elements_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/api/indicatorTypes.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_indicator_types_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/api/indicators.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_indicators_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/api/dataSets.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_datasets_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/api/organisationUnits.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_orgunits_response,
            status=200,
        )

        for model in (DataElement, IndicatorType, Indicator, DataSet, OrganisationUnit):
            self.assertEqual(model.objects.all().count(), 0)

        class MockLogger:
            def __init__(self):
                self.logs = []

            def info(self, *args):
                logger.info(args[0] % args[1:])
                self.logs.append(args)

        with patch(
            "hexa.plugins.connector_dhis2.models.logger", MockLogger()
        ) as mock_logger:
            self.assertTrue(len(mock_logger.logs) == 0)
            self.DHIS2_INSTANCE_PLAY.sync()
            self.assertTrue(len(mock_logger.logs) > 0)

        for model in (DataElement, IndicatorType, Indicator, DataSet):
            self.assertTrue(model.objects.all().count() > 0)

        # Let's make sure that the last_synced_at at the index level matches the instance last_synced_at
        first_data_element = DataElement.objects.filter(
            instance=self.DHIS2_INSTANCE_PLAY
        ).first()
        self.assertEqual(
            first_data_element.index.last_synced_at,
            self.DHIS2_INSTANCE_PLAY.start_synced_at,
        )
        # sync should take less than 10s
        self.assertTrue(
            (
                self.DHIS2_INSTANCE_PLAY.last_synced_at
                - self.DHIS2_INSTANCE_PLAY.start_synced_at
            )
            < timedelta(seconds=10)
        )


class DHIS2SyncInstanceSplitTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DHIS2_INSTANCE_PLAY1 = Instance.objects.create(
            url="https://play1.dhis2.org.invalid",
            slug="invalid1",
            api_credentials=Credentials.objects.create(
                api_url="https://play1.dhis2.org.invalid",
                username="test_username",
                password="test_password",
            ),
        )
        cls.DHIS2_INSTANCE_PLAY2 = Instance.objects.create(
            url="https://play2.dhis2.org.invalid",
            slug="invalid2",
            api_credentials=Credentials.objects.create(
                api_url="https://play2.dhis2.org.invalid",
                username="test_username",
                password="test_password",
            ),
        )

    @responses.activate
    def test_sync_same_org_units(self):
        responses.add(
            responses.GET,
            "https://play1.dhis2.org.invalid/api/organisationUnits.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_orgunits_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://play2.dhis2.org.invalid/api/organisationUnits.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_orgunits_response,
            status=200,
        )

        # each mock page contains 2 org unit. two instances with the same data should generate two separate
        # set of org units (or any other dhis2 object for that matter) -> we should have 4 org units at the end
        self.assertEqual(OrganisationUnit.objects.all().count(), 0)
        client_play1 = Dhis2Client(
            url=self.DHIS2_INSTANCE_PLAY1.api_credentials.api_url,
            username=self.DHIS2_INSTANCE_PLAY1.api_credentials.username,
            password=self.DHIS2_INSTANCE_PLAY1.api_credentials.password,
        )
        client_play2 = Dhis2Client(
            url=self.DHIS2_INSTANCE_PLAY2.api_credentials.api_url,
            username=self.DHIS2_INSTANCE_PLAY2.api_credentials.username,
            password=self.DHIS2_INSTANCE_PLAY2.api_credentials.password,
        )

        sync_from_dhis2_results(
            model_class=OrganisationUnit,
            instance=self.DHIS2_INSTANCE_PLAY1,
            results=client_play1.fetch_organisation_units(),
        )
        sync_from_dhis2_results(
            model_class=OrganisationUnit,
            instance=self.DHIS2_INSTANCE_PLAY2,
            results=client_play2.fetch_organisation_units(),
        )
        self.assertEqual(OrganisationUnit.objects.all().count(), 4)

    @responses.activate
    def test_sync_same_indicator_types(self):
        """We can have references (such as indicator types) that are common across instances. The system
        should handle it properly.
        """
        IndicatorType.objects.create(
            instance=self.DHIS2_INSTANCE_PLAY1,
            dhis2_id="bWuNrMHEoZ0",
            external_access=True,
            number=True,
            factor=2,
            favorite=False,
            created=timezone.now(),
            last_updated=timezone.now(),
        )
        IndicatorType.objects.create(
            instance=self.DHIS2_INSTANCE_PLAY2,
            dhis2_id="bWuNrMHEoZ0",
            external_access=True,
            number=True,
            factor=2,
            favorite=False,
            created=timezone.now(),
            last_updated=timezone.now(),
        )
        responses.add(
            responses.GET,
            "https://play2.dhis2.org.invalid/api/indicators.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_indicators_response,
            status=200,
        )

        client_play2 = Dhis2Client(
            url=self.DHIS2_INSTANCE_PLAY2.api_credentials.api_url,
            username=self.DHIS2_INSTANCE_PLAY2.api_credentials.username,
            password=self.DHIS2_INSTANCE_PLAY2.api_credentials.password,
        )
        # This should not trigger an error, even if we have two indicator types with the same id (but different
        # instances)
        sync_from_dhis2_results(
            model_class=Indicator,
            instance=self.DHIS2_INSTANCE_PLAY2,
            results=client_play2.fetch_indicators(),
        )
        self.assertEqual(
            2, Indicator.objects.filter(indicator_type__dhis2_id="bWuNrMHEoZ0").count()
        )


class Dhis2SyncDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            url="https://play.dhis2.org.invalid",
        )

    def test_delete_data_element(self):
        """If DEs disapear from remote instance, sync should delete DEs+index in OH"""
        common_info = {
            "externalAccess": False,
            "favorite": False,
            "created": "2022-01-01T00:00:00",
            "lastUpdated": "2022-01-01T00:00:00",
            "code": "CODE",
            "domainType": "AGGREGATE",
            "valueType": "TEXT",
            "aggregationType": "AVERAGE",
        }
        DataElement.objects.create(
            dhis2_id="XXX",
            name="XXX",
            instance=self.DHIS2_INSTANCE_PLAY,
            external_access=False,
            favorite=False,
            created="2022-01-01T00:00:00Z",
            last_updated="2022-01-01T00:00:00Z",
        )
        self.assertEqual(
            DataElement.objects.filter(instance=self.DHIS2_INSTANCE_PLAY).count(), 1
        )
        dsr = sync_from_dhis2_results(
            model_class=DataElement,
            instance=self.DHIS2_INSTANCE_PLAY,
            results=[
                DataElementResult(dict({"id": "XXX", "name": "XXX"}, **common_info)),
                DataElementResult(dict({"id": "YYY", "name": "YYY"}, **common_info)),
            ],
        )
        self.assertEqual(dsr.deleted, 0)
        self.assertEqual(
            DataElement.objects.filter(instance=self.DHIS2_INSTANCE_PLAY).count(), 2
        )
        dsr = sync_from_dhis2_results(
            model_class=DataElement,
            instance=self.DHIS2_INSTANCE_PLAY,
            results=[
                DataElementResult(dict({"id": "YYY", "name": "YYY"}, **common_info)),
            ],
        )
        self.assertEqual(dsr.deleted, 2)  # 2 because 1 DE + 1 index
        self.assertEqual(
            DataElement.objects.filter(instance=self.DHIS2_INSTANCE_PLAY).count(), 1
        )
