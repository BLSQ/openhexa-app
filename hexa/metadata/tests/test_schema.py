from django.contrib.contenttypes.models import ContentType

from hexa.core.test import GraphQLTestCase
from hexa.datasets.models import Dataset, DatasetVersionFile
from hexa.metadata.models import MetadataAttribute
from hexa.metadata.tests.testutils import MetadataTestMixin, encode_base_64
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
        opaque_id = encode_base_64(
            str(file.id)
            + ":"
            + str(ContentType.objects.get_for_model(DatasetVersionFile).id)
        )
        self.assertEqual(
            r_before["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "opaqueId": opaque_id,
                    "attributes": [],
                }
            },
        )
        r_add = self.run_query(
            self.queries["add_metadata_attribute"],
            {
                "input": {
                    "targetId": opaque_id,
                    "key": "descriptions",
                    "value": "test",
                }
            },
        )
        self.assertEqual(
            r_add["data"], {"addMetadataAttribute": {"success": True, "errors": []}}
        )

        r_after = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(
            r_after["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "opaqueId": opaque_id,
                    "attributes": [
                        {"key": "descriptions", "value": "test", "system": False}
                    ],
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
            object_content_type_id=ContentType.objects.get_for_model(
                DatasetVersionFile
            ).id,
            object_id=file.id,
        )
        opaque_id = encode_base_64(
            str(file.id)
            + ":"
            + str(ContentType.objects.get_for_model(DatasetVersionFile).id)
        )
        r_before = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(
            r_before["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "opaqueId": opaque_id,
                    "attributes": [{"key": "key1", "value": "value1", "system": True}],
                }
            },
        )
        r_delete = self.run_query(
            self.queries["delete_metadata_attribute"],
            {
                "input": {
                    "targetId": opaque_id,
                    "key": metadataAttribute.key,
                }
            },
        )
        self.assertEqual(
            r_delete["data"],
            {"deleteMetadataAttribute": {"success": True, "errors": []}},
        )
        r_after = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(
            r_after["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "opaqueId": opaque_id,
                    "attributes": [],
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
        opaque_id = encode_base_64(
            str(file.id)
            + ":"
            + str(ContentType.objects.get_for_model(DatasetVersionFile).id)
        )
        metadataAttribute = MetadataAttribute.objects.create(
            key="key1",
            value="value1",
            system=True,
            object_content_type_id=ContentType.objects.get_for_model(
                DatasetVersionFile
            ).id,
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
                    "opaqueId": opaque_id,
                    "attributes": [
                        {
                            "key": metadataAttribute.key,
                            "value": metadataAttribute.value,
                            "system": metadataAttribute.system,
                        }
                    ],
                }
            },
        )
        r_edit = self.run_query(
            self.queries["edit_metadata_attribute"],
            {
                "input": {
                    "targetId": opaque_id,
                    "key": metadataAttribute.key,
                    "value": "anotherValue",
                }
            },
        )
        self.assertEqual(
            r_edit["data"], {"editMetadataAttribute": {"success": True, "errors": []}}
        )
        r_after = self.run_query(
            self.queries["get_metadata_for_file"], {"id": str(file.id)}
        )
        self.assertEqual(
            r_after["data"],
            {
                "datasetVersionFile": {
                    "filename": "file.csv",
                    "opaqueId": opaque_id,
                    "attributes": [
                        {
                            "key": metadataAttribute.key,
                            "value": "anotherValue",
                            "system": False,
                        }
                    ],
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

        opaque_id = encode_base_64(
            str(dataset.id) + ":" + str(ContentType.objects.get_for_model(Dataset).id)
        )

        r_before = self.run_query(
            self.queries["get_metadata_for_dataset"], {"id": str(dataset.id)}
        )
        self.assertEqual(
            r_before["data"],
            {
                "dataset": {
                    "opaqueId": opaque_id,
                    "attributes": [],
                }
            },
        )

        r_add = self.run_query(
            self.queries["add_metadata_attribute"],
            {
                "input": {
                    "targetId": opaque_id,
                    "key": "descriptions",
                    "value": "test",
                }
            },
        )
        self.assertEqual(
            r_add["data"], {"addMetadataAttribute": {"success": True, "errors": []}}
        )

        r_after = self.run_query(
            self.queries["get_metadata_for_dataset"], {"id": str(dataset.id)}
        )
        self.assertEqual(
            r_after["data"],
            {
                "dataset": {
                    "opaqueId": opaque_id,
                    "attributes": [
                        {"key": "descriptions", "value": "test", "system": False}
                    ],
                }
            },
        )

    queries = {
        "get_metadata_for_file": """
            query GetObjectMetadata($id: ID!) {
                  datasetVersionFile(id: $id) {
                    filename
                    opaqueId
                    attributes {
                          key, value, system
                        }
                  }
                }
            """,
        "get_metadata_for_dataset": """
        query GetObjectMetadata($id: ID!) {
              dataset(id: $id) {
                opaqueId
                attributes {
                      key, value, system
                }
              }
            }
        """,
        "add_metadata_attribute": """
            mutation AddMetadataToFile($input: CreateMetadataAttributeInput!){
              addMetadataAttribute(input: $input) {
                success
                errors
              }
            }
            """,
        "delete_metadata_attribute": """
            mutation DeleteMetadataFromFile($input: DeleteMetadataAttributeInput!){
              deleteMetadataAttribute(input: $input) {
                success
                errors
              }
            }
            """,
        "edit_metadata_attribute": """
            mutation editMetadataOnFile($input: EditMetadataAttributeInput!){
              editMetadataAttribute(input: $input) {
                success
                errors
              }
            }
            """,
    }
