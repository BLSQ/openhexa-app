from logging import getLogger
from unittest.mock import patch

import responses
from django import test
from django.utils import timezone

from hexa.catalog.models import Index
from hexa.user_management.models import Membership, Team, User

from ..api import Dhis2Client
from ..models import (
    Credentials,
    DataElement,
    DataSet,
    Indicator,
    IndicatorType,
    Instance,
    InstancePermission,
    OrganisationUnit,
)
from ..sync import sync_from_dhis2_results
from .mock_data import (
    mock_data_elements_response,
    mock_datasets_response,
    mock_indicator_types_response,
    mock_indicators_response,
    mock_info_json,
    mock_orgunits_response,
)

logger = getLogger(__name__)


class ConnectorDhis2Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            url="https://play.dhis2.org.invalid",
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


class PermissionTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DHIS2A = Instance.objects.create(url="https://play1.dhis2.org.invalid")
        cls.DHIS2B = Instance.objects.create(url="https://play2.dhis2.org.invalid")
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


class DHIS2SyncTest(test.TestCase):
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
            self.DHIS2_INSTANCE_PLAY.last_synced_at,
        )


class DHIS2SyncInstanceSplitTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DHIS2_INSTANCE_PLAY1 = Instance.objects.create(
            url="https://play1.dhis2.org.invalid",
            api_credentials=Credentials.objects.create(
                api_url="https://play1.dhis2.org.invalid",
                username="test_username",
                password="test_password",
            ),
        )
        cls.DHIS2_INSTANCE_PLAY2 = Instance.objects.create(
            url="https://play2.dhis2.org.invalid",
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

        for results_batch in client_play1.fetch_organisation_units():
            sync_from_dhis2_results(
                model_class=OrganisationUnit,
                instance=self.DHIS2_INSTANCE_PLAY1,
                results=results_batch,
            )
        for results_batch in client_play2.fetch_organisation_units():
            sync_from_dhis2_results(
                model_class=OrganisationUnit,
                instance=self.DHIS2_INSTANCE_PLAY2,
                results=results_batch,
            )
        self.assertEqual(OrganisationUnit.objects.all().count(), 4)

    @responses.activate
    def test_sync_same_indicator_types(self):
        """We can have references (such as indicator types) that are common across instances. The system
        should handle it properly."""

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
        for results_batch in client_play2.fetch_indicators():
            # This should not trigger an error, even if we have two indicator types with the same id (but different
            # instances)
            sync_from_dhis2_results(
                model_class=Indicator,
                instance=self.DHIS2_INSTANCE_PLAY2,
                results=results_batch,
            )
        self.assertEqual(
            2, Indicator.objects.filter(indicator_type__dhis2_id="bWuNrMHEoZ0").count()
        )
