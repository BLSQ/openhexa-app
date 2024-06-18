from django.contrib.contenttypes.models import ContentType

from hexa.core.test import GraphQLTestCase
from hexa.datasets.models import DatasetVersionFile
from hexa.metadata.models import MetadataAttribute
from hexa.metadata.tests.testutils import MetadataTestMixin
from hexa.workspaces.models import WorkspaceMembershipRole


class MetadataTest(GraphQLTestCase, MetadataTestMixin):
    def test_permission_denied_to_view(self):
        user = self.create_user(email="superuser@blsq.com", is_superuser=True)
        user2 = self.create_user(email="notsu@blsq.com")
        workspace = self.create_workspace(
            principal=user, name="workspace", description="desc"
        )
        dataset = self.create_dataset(
            principal=user, description="ds", name="Dataset", workspace=workspace
        )
        self.create_dataset_version(principal=user, dataset=dataset)
        self.client.force_login(user2)
        file = DatasetVersionFile.objects.create(
            dataset_version=dataset.latest_version,
            uri=dataset.latest_version.get_full_uri("file.csv"),
            created_by=user,
        )
        file.add_attribute(key="height", value="188cm", system=False)
        r_before = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(r_before["data"], {"datasetVersionFile": None})

    def test_adding_metadata_to_file(self):
        user = self.create_user(email="superuser@blsq.com", is_superuser=True)
        user2 = self.create_user(email="notsu@blsq.com")
        workspace = self.create_workspace(
            principal=user, name="workspace", description="desc"
        )
        self.join_workspace(user2, workspace, WorkspaceMembershipRole.EDITOR)
        dataset = self.create_dataset(
            principal=user2, description="ds", name="Dataset", workspace=workspace
        )
        self.create_dataset_version(principal=user2, dataset=dataset)
        self.client.force_login(user2)
        file = DatasetVersionFile.objects.create(
            dataset_version=dataset.latest_version,
            uri=dataset.latest_version.get_full_uri("file.csv"),
            created_by=user,
        )

        r_before = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )

        self.assertEqual(
            r_before["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "metadata": {
                        "id": file.extended_id,
                        "attributes": [],
                        "object": {
                            "__typename": "DatasetVersionFile",
                            "id": str(file.id),
                            "uri": str(file.uri),
                        },
                    },
                }
            },
        )
        r_add = self.run_query(
            self.queries["add_metadata_attribute"],
            {
                "input": {
                    "extendedId": file.extended_id,
                    "key": "descriptions",
                    "value": "test",
                }
            },
        )
        self.assertEqual(
            r_add["data"], {"addMetadataToObject": {"success": True, "errors": []}}
        )

        r_after = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(
            r_after["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "metadata": {
                        "id": file.extended_id,
                        "object": {
                            "__typename": "DatasetVersionFile",
                            "id": str(file.id),
                            "uri": str(file.uri),
                        },
                        "attributes": [
                            {"key": "descriptions", "value": "test", "system": False}
                        ],
                    },
                }
            },
        )

    def test_delete_metadata_from_file(self):
        user = self.create_user(email="superuser@blsq.com", is_superuser=True)
        user2 = self.create_user(email="notsu@blsq.com")
        workspace = self.create_workspace(
            principal=user, name="workspace", description="desc"
        )
        self.join_workspace(user2, workspace, WorkspaceMembershipRole.EDITOR)
        dataset = self.create_dataset(
            principal=user, description="ds", name="Dataset", workspace=workspace
        )
        self.create_dataset_version(principal=user, dataset=dataset)
        self.client.force_login(user)
        file = DatasetVersionFile.objects.create(
            dataset_version=dataset.latest_version,
            uri=dataset.latest_version.get_full_uri("file.csv"),
            created_by=user,
        )

        metadataAttribute = MetadataAttribute.objects.create(
            key="key1",
            value="value1",
            system=True,
            content_type=ContentType.objects.get_for_model(DatasetVersionFile),
            object_id=file.id,
        )
        r_before = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(
            r_before["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "metadata": {
                        "id": file.extended_id,
                        "object": {
                            "__typename": "DatasetVersionFile",
                            "id": str(file.id),
                            "uri": str(file.uri),
                        },
                        "attributes": [
                            {"key": "key1", "value": "value1", "system": True}
                        ],
                    },
                }
            },
        )
        r_delete = self.run_query(
            self.queries["delete_metadata_attribute"],
            {
                "input": {
                    "extendedId": file.extended_id,
                    "key": metadataAttribute.key,
                }
            },
        )
        self.assertEqual(
            r_delete["data"],
            {"deleteMetadataFromObject": {"success": True, "errors": []}},
        )
        r_after = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(
            r_after["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "metadata": {
                        "id": file.extended_id,
                        "object": {
                            "__typename": "DatasetVersionFile",
                            "id": str(file.id),
                            "uri": str(file.uri),
                        },
                        "attributes": [],
                    },
                }
            },
        )

    def test_edit_metadata_on_file(self):
        user = self.create_user(email="superuser@blsq.com", is_superuser=True)
        user2 = self.create_user(email="notsu@blsq.com")
        workspace = self.create_workspace(
            principal=user, name="workspace", description="desc"
        )
        self.join_workspace(user2, workspace, WorkspaceMembershipRole.EDITOR)
        dataset = self.create_dataset(
            principal=user, description="ds", name="Dataset", workspace=workspace
        )
        self.create_dataset_version(principal=user, dataset=dataset)
        self.client.force_login(user)
        file = DatasetVersionFile.objects.create(
            dataset_version=dataset.latest_version,
            uri=dataset.latest_version.get_full_uri("file.csv"),
            created_by=user,
        )
        metadataAttribute = MetadataAttribute.objects.create(
            key="key1",
            value="originalValue",
            system=True,
            content_type=ContentType.objects.get_for_model(DatasetVersionFile),
            object_id=file.id,
        )

        r_before = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(
            r_before["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "metadata": {
                        "id": file.extended_id,
                        "object": {
                            "__typename": "DatasetVersionFile",
                            "id": str(file.id),
                            "uri": str(file.uri),
                        },
                        "attributes": [
                            {
                                "key": metadataAttribute.key,
                                "value": metadataAttribute.value,
                                "system": metadataAttribute.system,
                            }
                        ],
                    },
                }
            },
        )
        r_edit = self.run_query(
            self.queries["edit_metadata_attribute"],
            {
                "input": {
                    "extendedId": file.extended_id,
                    "key": metadataAttribute.key,
                    "value": "anotherValue",
                }
            },
        )
        self.assertEqual(
            r_edit["data"], {"editMetadataForObject": {"success": True, "errors": []}}
        )
        r_after = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(
            r_after["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "metadata": {
                        "id": file.extended_id,
                        "object": {
                            "__typename": "DatasetVersionFile",
                            "id": str(file.id),
                            "uri": str(file.uri),
                        },
                        "attributes": [
                            {
                                "key": metadataAttribute.key,
                                "value": "anotherValue",
                                "system": False,
                            }
                        ],
                    },
                }
            },
        )

    def test_adding_metadata_to_dataset(self):
        user = self.create_user(email="superuser@blsq.com", is_superuser=True)
        user2 = self.create_user(email="notsu@blsq.com")
        workspace = self.create_workspace(
            principal=user, name="workspace", description="desc"
        )
        self.join_workspace(user2, workspace, WorkspaceMembershipRole.EDITOR)
        dataset = self.create_dataset(
            principal=user, description="ds", name="Dataset", workspace=workspace
        )
        self.create_dataset_version(principal=user, dataset=dataset)
        self.client.force_login(user)

        r_before = self.run_query(
            self.queries["get_metadata_for_dataset"], {"id": str(dataset.id)}
        )
        self.assertEqual(
            r_before["data"],
            {
                "dataset": {
                    "id": str(dataset.id),
                    "extendedId": dataset.extended_id,
                    "metadata": {
                        "id": dataset.extended_id,
                        "attributes": [],
                        "object": {
                            "__typename": "Dataset",
                            "id": str(dataset.id),
                            "name": "Dataset",
                        },
                    },
                }
            },
        )

        r_add = self.run_query(
            self.queries["add_metadata_attribute"],
            {
                "input": {
                    "extendedId": dataset.extended_id,
                    "key": "descriptions",
                    "value": "test",
                }
            },
        )
        self.assertEqual(
            r_add["data"], {"addMetadataToObject": {"success": True, "errors": []}}
        )

        r_after = self.run_query(
            self.queries["get_metadata_for_dataset"], {"id": str(dataset.id)}
        )
        self.assertEqual(
            r_after["data"],
            {
                "dataset": {
                    "id": str(dataset.id),
                    "extendedId": dataset.extended_id,
                    "metadata": {
                        "id": dataset.extended_id,
                        "object": {
                            "__typename": "Dataset",
                            "id": str(dataset.id),
                            "name": dataset.name,
                        },
                        "attributes": [
                            {"key": "descriptions", "value": "test", "system": False}
                        ],
                    },
                }
            },
        )

    queries = {
        "get_metadata_for_file": """
            query GetObjectMetadata($id: ID!) {
                  datasetVersionFile(id: $id) {
                    filename
                    metadata
                        {
                        id
                        object{
                          __typename
                          ... on DatasetVersionFile {
                            id
                            uri
                          }
                          ... on Dataset {
                            id
                            name
                          }
                          ... on DatasetVersion {
                            id
                          }
                        }
                        attributes {
                          key, value, system
                        }
                      }
                  }
                }
            """,
        "get_metadata_for_dataset": """
        query GetObjectMetadata($id: ID!) {
              dataset(id: $id) {
                id
                extendedId
                metadata
                    {
                    id
                    object{
                      __typename
                      ... on DatasetVersionFile {
                        id
                        uri
                      }
                      ... on Dataset {
                        id
                        name
                      }
                      ... on DatasetVersion {
                        id
                      }
                    }
                    attributes {
                      key, value, system
                    }
                  }
              }
            }
        """,
        "add_metadata_attribute": """
            mutation AddMetadataToFile($input: MetadataAttributeInput!){
              addMetadataToObject(input: $input) {
                success
                errors
              }
            }
            """,
        "delete_metadata_attribute": """
            mutation DeleteMetadataFromFile($input: DeleteMetadataAttributeInput!){
              deleteMetadataFromObject(input: $input) {
                success
                errors
              }
            }
            """,
        "edit_metadata_attribute": """
            mutation editMetadataOnFile($input: MetadataAttributeInput!){
              editMetadataForObject(input: $input) {
                success
                errors
              }
            }
            """,
    }
