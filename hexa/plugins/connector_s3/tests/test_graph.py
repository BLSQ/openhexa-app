from unittest import skip

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_s3.models import (
    Bucket,
    BucketPermission,
    Object,
)
from hexa.user_management.models import User, Team, Membership, Organization


class S3GraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )
        Membership.objects.create(team=cls.TEAM, user=cls.USER)
        cls.BUCKET = Bucket.objects.create(name="test-bucket")
        BucketPermission.objects.create(team=cls.TEAM, bucket=cls.BUCKET)

    @skip("Deactivated for now")
    def test_s3bucket(self):
        self.maxDiff = None
        self.client.force_login(self.USER)
        o = Organization.objects.create(name="Bluesquare")

        level1 = Object.objects.create(
            bucket=self.BUCKET,
            size=1234,
            name="name1",
            description="desc",
            locale="en",
            key="test-bucket/dir1/",
            parent_key="test-bucket/",
            type="directory",
            storage_class="GLACIER",
            owner=o,
        )

        level2 = Object.objects.create(
            bucket=self.BUCKET,
            size=1234,
            name="dir2/",
            description="desc",
            locale="en",
            key="test-bucket/dir1/dir2/",
            parent_key="test-bucket/dir1/",
            type="directory",
            storage_class="GLACIER",
            owner=o,
        )

        Object.objects.create(
            bucket=self.BUCKET,
            size=1234,
            name="name3",
            description="desc",
            locale="en",
            key="test-bucket/dir1/dir2/file1.csv",
            parent_key="test-bucket/dir1/dir2/",
            type="file",
            storage_class="GLACIER",
            owner=o,
        )

        r = self.run_query(
            """
                query s3Bucket($id: String!) {
                  s3Bucket(id: $id) {
                    objects(page: 1) {
                      items {
                        owner {
                          name
                        }
                        name
                        s3Extension
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
                        s3Key
                        s3Size
                        s3Type
                        objects(page: 1) {
                          items {
                            name
                            s3Key
                            s3Extension
                            objects(page: 1) {
                              items {
                                name
                                s3Key
                                s3Extension
                                objects(page: 1) {
                                  items {
                                    id
                                    s3Extension
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
            """,
            {"id": str(self.BUCKET.id)},
        )

        self.assertEqual(
            r["data"]["s3Bucket"]["objects"]["items"][0],
            {
                "owner": {"name": "Bluesquare"},
                "name": "dir1/",
                "description": "desc",
                "countries": [],
                "locale": "en",
                "tags": [],
                "bucket": {"name": ""},
                "s3Key": "test-bucket/dir1/",
                "s3Size": 1234,
                "s3Type": "directory",
                "s3Extension": "",
                "objects": {
                    "items": [
                        {
                            "name": "dir2/",
                            "s3Key": "test-bucket/dir1/dir2/",
                            "s3Extension": "",
                            "objects": {
                                "items": [
                                    {
                                        "name": "file1.csv",
                                        "s3Key": "test-bucket/dir1/dir2/file1.csv",
                                        "s3Extension": "csv",
                                        "objects": {"items": []},
                                    }
                                ]
                            },
                        }
                    ]
                },
            },
        )

    @skip("Deactivated for now")
    def test_s3objects(self):
        self.maxDiff = None
        self.client.force_login(self.USER)

        o1 = Object.objects.create(
            bucket=self.BUCKET,
            size=1234,
            description="desc",
            locale="en",
            key="test-bucket/dir1/",
            parent_key="test-bucket/",
            type="directory",
            storage_class="GLACIER",
        )

        o2 = Object.objects.create(
            bucket=self.BUCKET,
            size=1234,
            description="desc",
            locale="en",
            key="test-bucket/dir1/test.csv",
            parent_key="test-bucket/",
            type="file",
            storage_class="GLACIER",
        )

        r = self.run_query(
            """
                query s3Objects($bucketS3Name: String!, $page: Int!) {
                  s3Objects(bucketS3Name: $bucketS3Name, page: $page) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                      name
                    }
                  }
                }
            """,
            {"bucketS3Name": str(self.BUCKET.name), "page": 1},
        )

        self.assertEqual(
            r,
            {
                "data": {
                    "s3Objects": {
                        "pageNumber": 1,
                        "totalPages": 1,
                        "totalItems": 2,
                        "items": [
                            {"id": str(o1.id), "name": "dir1/"},
                            {"id": str(o2.id), "name": "test.csv"},
                        ],
                    }
                }
            },
        )
