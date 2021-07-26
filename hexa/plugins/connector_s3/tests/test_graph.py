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
            "jim@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )
        Membership.objects.create(team=cls.TEAM, user=cls.USER)
        cls.BUCKET = Bucket.objects.create(s3_name="test-bucket")
        BucketPermission.objects.create(team=cls.TEAM, bucket=cls.BUCKET)

    def test_s3bucket(self):
        self.maxDiff = None
        self.client.force_login(self.USER)
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
            s3_key="/dir1/dir2/file1.csv",
            s3_type="directory",
            s3_storage_class="GLACIER",
            s3_name="s3Name3",
            owner=o,
            parent=level2,
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

        self.assertEquals(
            r["data"]["s3Bucket"]["objects"]["items"][0],
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
                "s3Extension": "",
                "objects": {
                    "items": [
                        {
                            "name": "name2",
                            "s3Key": "/dir1/dir2/",
                            "s3Extension": "",
                            "objects": {
                                "items": [
                                    {
                                        "name": "name3",
                                        "s3Key": "/dir1/dir2/file1.csv",
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

    def test_s3objects(self):
        self.maxDiff = None
        self.client.force_login(self.USER)

        o1 = Object.objects.create(
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
        )

        o2 = Object.objects.create(
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
        )

        r = self.run_query(
            """
                query s3Objects($bucketId: String!, $page: Int!) {
                  s3Objects(bucketId: $bucketId, page: $page) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                      name
                      s3Name
                    }
                  }
                }
            """,
            {"bucketId": str(self.BUCKET.id), "page": 1},
        )

        self.assertEquals(
            r,
            {
                "data": {
                    "s3Objects": {
                        "pageNumber": 1,
                        "totalPages": 1,
                        "totalItems": 2,
                        "items": [
                            {"id": str(o1.id), "name": "name1", "s3Name": "s3Name1"},
                            {"id": str(o2.id), "name": "name2", "s3Name": "s3Name2"},
                        ],
                    }
                }
            },
        )
