from django import test
from django.urls import reverse
from unittest import skip
import json

from hexa.catalog.models import CatalogIndex
from hexa.plugins.connector_s3.models import (
    Credentials,
    Bucket,
    BucketPermission,
    Object,
)
from hexa.user_management.models import User, Team, Membership, Organization


def query(client, payload):
    return json.loads(
        client.post(
            "/graphql/",
            json.dumps(
                {
                    "operationName": None,
                    "variables": {},
                    "query": payload,
                }
            ),
            content_type="application/json",
        ).content
    )


class ConnectorS3Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )
        Membership.objects.create(team=cls.TEAM, user=cls.USER)
        cls.API_CREDENTIALS = Credentials.objects.create(
            username="app-iam-username",
            access_key_id="FOO",
            secret_access_key="BAR",
            default_region="us-west-2",
        )
        cls.BUCKET = Bucket.objects.create(s3_name="test-bucket")
        BucketPermission.objects.create(team=cls.TEAM, bucket=cls.BUCKET)

    @skip("Deactivated for now - mocks needed")
    def test_credentials_200(self):
        self.client.login(email="jim@bluesquarehub.com", password="regular")
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("username", response_data)
        self.assertEqual("jim@bluesquarehub.com", response_data["username"])
        self.assertIn("env", response_data)
        self.assertEqual(
            {
                "S3_TEST_BUCKET_BUCKET_NAME": "test-bucket",
                "S3_TEST_BUCKET_ACCESS_KEY_ID": "FOO",
                "S3_TEST_BUCKET_SECRET_ACCESS_KEY": "BAR",
            },
            response_data["env"],
        )

    def test_bucket_delete(self):
        """Deleting a bucket should delete its index as well"""

        bucket = Bucket.objects.create(s3_name="some-bucket")
        bucket_id = bucket.id
        self.assertEqual(1, CatalogIndex.objects.filter(object_id=bucket_id).count())
        bucket.delete()
        self.assertEqual(0, CatalogIndex.objects.filter(object_id=bucket_id).count())

    def test_graph(self):
        self.maxDiff = None
        self.client.login(email="jim@bluesquarehub.com", password="regular")
        o = Organization.objects.create(name="Bluesquare")

        level1 = Object.objects.create(
            bucket=self.BUCKET,
            s3_size=1234,
            name="name1",
            short_name="short1",
            description="desc",
            locale="en",
            s3_key="/dir1",
            s3_type="directory",
            s3_storage_class="GLACIER",
            s3_name="s3Name1",
            owner=o,
            s3_mime_type="application/octet-stream",
        )

        level2 = Object.objects.create(
            bucket=self.BUCKET,
            s3_size=1234,
            name="name2",
            short_name="short2",
            description="desc",
            locale="en",
            s3_key="/dir1/dir2/",
            s3_type="directory",
            s3_storage_class="GLACIER",
            s3_name="s3Name2",
            owner=o,
            parent=level1,
        )

        Object.objects.create(
            bucket=self.BUCKET,
            s3_size=1234,
            name="name3",
            short_name="short3",
            description="desc",
            locale="en",
            s3_key="/dir1/dir2/file1",
            s3_type="directory",
            s3_storage_class="GLACIER",
            s3_name="s3Name3",
            owner=o,
            parent=level2,
        )

        r = query(
            self.client,
            """
                query {
                  s3Bucket(id: "%s") {
                    Objects(page: 1) {
                      items {
                        owner {
                          name
                        }
                        name
                        s3MimeType
                        shortName
                        description
                        countries {
                          name
                        }
                        locale
                        tags {
                          name
                        }
                        bucket {
                          name
                        }
                        parent {
                          name
                        }
                        s3Key
                        s3Size
                        s3StorageClass
                        s3Type
                        s3Name
                        Objects(page: 1) {
                          items {
                            name
                            s3Key
                            Objects(page: 1) {
                              items {
                                name
                                s3Key
                                Objects(page: 1) {
                                  items {id
                                    name
                                    s3Key
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
            """
            % self.BUCKET.id,
        )

        self.assertEquals(
            r["data"]["s3Bucket"]["Objects"]["items"][0],
            {
                "owner": {"name": "Bluesquare"},
                "name": "name1",
                "shortName": "short1",
                "description": "desc",
                "countries": [],
                "locale": "en",
                "tags": [],
                "bucket": {"name": ""},
                "parent": None,
                "s3Key": "/dir1",
                "s3Size": 1234,
                "s3StorageClass": "GLACIER",
                "s3Type": "directory",
                "s3Name": "s3Name1",
                "s3MimeType": "application/octet-stream",
                "Objects": {
                    "items": [
                        {
                            "name": "name2",
                            "s3Key": "/dir1/dir2/",
                            "Objects": {
                                "items": [
                                    {
                                        "name": "name3",
                                        "s3Key": "/dir1/dir2/file1",
                                        "Objects": {"items": []},
                                    }
                                ]
                            },
                        }
                    ]
                },
            },
        )
