from django.utils import timezone

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_dhis2.models import (
    DataElement,
    DataSet,
    Indicator,
    Instance,
    InstancePermission,
    OrganisationUnit,
)
from hexa.plugins.connector_s3.models import Bucket, BucketPermission
from hexa.user_management.models import Team, User


class CatalogSearchTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_BJORN = User.objects.create_user(
            "bjorn@bluesquarehub.com",
            "bjornbjorn",
        )
        cls.USER_KRISTEN = User.objects.create_user(
            "kristen@bluesquarehub.com",
            "kristen2000",
            is_superuser=True,
        )
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            url="https://play.dhis2.org", name="DHIS2 Play"
        )
        InstancePermission.objects.create(
            team=cls.TEAM, instance=cls.DHIS2_INSTANCE_PLAY
        )
        cls.ORGUNIT = OrganisationUnit.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="JFx4YWRDIyK",
            name="A geo zone",
            created=timezone.now(),
            last_updated=timezone.now(),
            path="JFx4YWRDIyK",
            leaf=True,
            external_access=False,
            favorite=False,
        )
        cls.DATASET = DataSet.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="1ceDA1fEcvX",
            name="A dataset",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
        )
        cls.DATA_ELEMENT_1 = DataElement.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="O1BccPF5yci",
            name="ANC First visit",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
        )
        cls.DATA_ELEMENT_2 = DataElement.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="eLW6jbvVcPZ",
            name="ANC Second visit",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
        )
        cls.DATA_ELEMENT_3 = DataElement.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="kmaHyZXMHCz",
            name="C-sections",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
        )
        cls.DATA_INDICATOR_1 = Indicator.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="xaG3AfYG2Ts",
            name="Ante-Natal Care visits",
            description="Uses different ANC data indicators",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
            annualized=False,
        )
        cls.DATA_INDICATOR_1_similar = Indicator.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="xaG3AfYG2TD",
            name="Ante-Natal Care visits",
            description="Uses different ANC data inTdicators",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
            annualized=False,
        )
        cls.DATA_INDICATOR_2 = Indicator.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="oNzq8duNBx6",
            name="Medical displays",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
            annualized=False,
        )
        cls.BUCKET = Bucket.objects.create(name="hexa-my-bucket-etc")
        BucketPermission.objects.create(bucket=cls.BUCKET, team=cls.TEAM)

    def test_search_anonymous(self):
        r = self.run_query(
            """
              query search {
                search(query: "") {
                  results {
                    rank
                  }
                }
              }
            """
        )
        self.assertEqual({"results": []}, r["data"]["search"])

    def test_search_empty(self):
        """Bjorn is not a superuser, he can see the catalog but it will be empty."""
        self.client.force_login(self.USER_BJORN)

        r = self.run_query(
            """
              query search {
                search(query: "anc") {
                  results {
                    rank
                  }
                  types {
                    value
                    label
                  }
                }
              }
            """
        )

        self.assertEqual({"results": [], "types": []}, r["data"]["search"])

    def test_search_no_query(self):
        """No query, no result."""
        self.client.force_login(self.USER_KRISTEN)

        r = self.run_query(
            """
              query search {
                search {
                  results {
                    rank
                  }
                  types {
                    value
                    label
                  }
                }
              }
            """
        )

        self.assertEqual(
            {
                "results": [],
                "types": [
                    {"label": "DHIS2 Data Element", "value": "dhis2_dataelement"},
                    {"label": "DHIS2 Data Set", "value": "dhis2_dataset"},
                    {"label": "DHIS2 Indicator", "value": "dhis2_indicator"},
                    {"label": "DHIS2 Instance", "value": "dhis2_instance"},
                    {
                        "label": "DHIS2 Organisation Unit",
                        "value": "dhis2_organisationunit",
                    },
                    {"label": "S3 Bucket", "value": "s3_bucket"},
                ],
            },
            r["data"]["search"],
        )

    def test_search_with_results(self):
        """As a superuser, Kristen can search for content."""
        self.client.force_login(self.USER_KRISTEN)

        r = self.run_query(
            """
          query search {
            search(query: "anc") {
              results {
                rank
              }
              types {
                value
                label
              }
            }
          }
        """
        )

        self.assertEqual(4, len(r["data"]["search"]["results"]))

    def test_dhis2_id(self):
        """As a user, Kristen can search for DHIS2 id and found dhis2 objects."""
        self.client.force_login(self.USER_KRISTEN)

        for q in ("JFx4YWRDIyK", "O1BccPF5yci", "xaG3AfYG2Ts", "1ceDA1fEcvX"):
            r = self.run_query(
                """
              query search ($query: String) {
                search(query: $query) {
                  results {
                    object {
                      ...on CatalogEntry {
                        objectId
                        datasource {
                          name
                        }
                      }
                    }
                    rank
                  }
                }
              }
            """,
                {"query": q},
            )
            results = r["data"]["search"]["results"]
            self.assertTrue(len(results) > 0)
            self.assertTrue(
                len(
                    [
                        i
                        for i in results
                        if i["object"]["datasource"]["name"]
                        == self.DHIS2_INSTANCE_PLAY.name
                    ]
                )
                > 0
            )

    def test_search_datasource_invalid(self):
        # we should not have any result for a datasource bucket but type instance
        self.client.force_login(self.USER_KRISTEN)
        r = self.run_query(
            """
          query search ($types: [String!], $datasourceIds: [String!]) {
            search(query: "play", types: $types, datasourceIds: $datasourceIds) {
              results {
                rank
              }
            }
          }
        """,
            {"types": ["type:dhis2_instance"], "datasourceIds": [str(self.BUCKET.id)]},
        )

        self.assertEqual(0, len(r["data"]["search"]["results"]))

    def test_search_instance_in_datasource(self):
        # we should have one response: the instance itself
        self.client.force_login(self.USER_KRISTEN)

        r = self.run_query(
            """
          query search ($types: [String!], $datasourceIds: [String!]) {
            search(query: "play", types: $types, datasourceIds: $datasourceIds) {
              results {
                rank
              }
            }
          }
        """,
            {
                "types": ["type:dhis2_instance"],
                "datasourceIds": [str(self.DHIS2_INSTANCE_PLAY.id)],
            },
        )

        self.assertEqual(1, len(r["data"]["search"]["results"]))

    def test_search_instance_elements(self):
        # we should have a lot a response: all ANC element from the instance
        self.client.force_login(self.USER_KRISTEN)

        r = self.run_query(
            """
          query search ($query: String, $types: [String!], $datasourceIds: [String!]) {
            search(query: $query, types: $types, datasourceIds: $datasourceIds) {
              results {
                rank
              }
            }
          }
        """,
            {
                "query": "ANC",
                "datasourceIds": [str(self.DHIS2_INSTANCE_PLAY.id)],
            },
        )

        self.assertTrue(len(r["data"]["search"]["results"]) > 1)

    def test_catalog_search_exact_word(self):
        # there is a similar data indicator name: indicator vs inTdicator -> fuzzy search should return 2, exact 1
        self.client.force_login(self.USER_KRISTEN)

        r = self.run_query(
            """
          query search ($query: String, $types: [String!], $datasourceIds: [String!]) {
            search(query: $query, types: $types, datasourceIds: $datasourceIds) {
              results {
                rank
              }
            }
          }
        """,
            {
                "query": "ANC data indicators",
            },
        )
        self.assertTrue(len(r["data"]["search"]["results"]) > 1)

        r = self.run_query(
            """
          query search ($query: String, $types: [String!], $datasourceIds: [String!]) {
            search(query: $query, types: $types, datasourceIds: $datasourceIds) {
              results {
                rank
              }
            }
          }
        """,
            {
                "query": '"ANC data indicators"',
            },
        )

        self.assertTrue(len(r["data"]["search"]["results"]) == 1)

    def test_search_datasource_ok(self):
        self.client.force_login(self.USER_KRISTEN)
        r = self.run_query(
            """
          query search ($query: String, $types: [String!], $datasourceIds: [String!]) {
            search(query: $query, types: $types, datasourceIds: $datasourceIds) {
              results {
                object {
                    ...on CatalogEntry {
                        objectId
                    }
                }
              }
            }
          }
        """,
            {
                "types": ["dhis2_instance"],
                "query": "play",
            },
        )
        self.assertTrue(len(r["data"]["search"]["results"]) == 1)
        self.assertEqual(
            {"object": {"objectId": str(self.DHIS2_INSTANCE_PLAY.id)}},
            r["data"]["search"]["results"][0],
        )

    def test_search_data_element_ok(self):
        self.client.force_login(self.USER_KRISTEN)
        r = self.run_query(
            """
          query search ($query: String, $types: [String!], $datasourceIds: [String!]) {
            search(query: $query, types: $types, datasourceIds: $datasourceIds) {
              results {
                object {
                    ...on CatalogEntry {
                        objectId
                    }
                }
              }
            }
          }
        """,
            {
                "types": ["dhis2_dataelement"],
                "query": "anc",
            },
        )
        self.assertTrue(len(r["data"]["search"]["results"]) == 2)
