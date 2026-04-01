from hexa.mcp.tools.pipelines import (
    get_pipeline,
    get_pipeline_run,
    list_pipelines,
    run_pipeline,
    update_pipeline,
)

from .testutils import MCPTestCase


class ListPipelinesTest(MCPTestCase):
    def test_list_pipelines(self):
        result = list_pipelines(
            user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug
        )
        pipelines = result["pipelines"]
        self.assertEqual(pipelines["totalItems"], 1)
        self.assertEqual(pipelines["items"][0]["code"], "test-pipeline")

    def test_list_pipelines_nonexistent_workspace(self):
        result = list_pipelines(user=self.USER_ADMIN, workspace_slug="nonexistent")
        self.assertEqual(result["pipelines"]["totalItems"], 0)

    def test_list_pipelines_no_access(self):
        result = list_pipelines(
            user=self.USER_OUTSIDER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(result["pipelines"]["totalItems"], 0)

    def test_list_pipelines_viewer(self):
        result = list_pipelines(
            user=self.USER_VIEWER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(result["pipelines"]["totalItems"], 1)


class GetPipelineTest(MCPTestCase):
    def test_get_pipeline(self):
        result = get_pipeline(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pipeline_code="test-pipeline",
        )
        self.assertEqual(result["code"], "test-pipeline")
        self.assertEqual(result["name"], "Test Pipeline")
        self.assertIsNotNone(result["currentVersion"])
        self.assertEqual(len(result["currentVersion"]["parameters"]), 1)
        self.assertEqual(result["currentVersion"]["parameters"][0]["code"], "param1")

    def test_get_pipeline_includes_files(self):
        result = get_pipeline(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pipeline_code="test-pipeline",
        )
        files = result["currentVersion"]["files"]
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["name"], "pipeline.py")
        self.assertEqual(files[0]["content"], 'print("hello")')

    def test_get_pipeline_includes_runs(self):
        result = get_pipeline(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pipeline_code="test-pipeline",
        )
        self.assertIn("runs", result)
        self.assertEqual(result["runs"]["totalItems"], 1)
        run = result["runs"]["items"][0]
        self.assertEqual(run["id"], str(self.PIPELINE_RUN.id))
        self.assertEqual(run["status"], "success")

    def test_get_pipeline_not_found(self):
        result = get_pipeline(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pipeline_code="nonexistent",
        )
        self.assertEqual(result, {"error": "Pipeline not found"})

    def test_get_pipeline_no_access(self):
        result = get_pipeline(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            pipeline_code="test-pipeline",
        )
        self.assertEqual(result, {"error": "Pipeline not found"})

    def test_get_pipeline_permissions(self):
        result = get_pipeline(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pipeline_code="test-pipeline",
        )
        self.assertIn("permissions", result)
        self.assertTrue(result["permissions"]["run"])
        self.assertTrue(result["permissions"]["update"])


class GetPipelineRunTest(MCPTestCase):
    def test_get_pipeline_run(self):
        result = get_pipeline_run(
            user=self.USER_ADMIN,
            run_id=str(self.PIPELINE_RUN.id),
        )
        self.assertEqual(result["id"], str(self.PIPELINE_RUN.id))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["config"], {"param1": "value1"})
        self.assertEqual(result["pipeline"]["code"], "test-pipeline")

    def test_get_pipeline_run_no_access(self):
        result = get_pipeline_run(
            user=self.USER_OUTSIDER,
            run_id=str(self.PIPELINE_RUN.id),
        )
        self.assertEqual(result, {"error": "Pipeline run not found"})

    def test_get_pipeline_run_not_found(self):
        result = get_pipeline_run(
            user=self.USER_ADMIN,
            run_id="00000000-0000-0000-0000-000000000000",
        )
        self.assertEqual(result, {"error": "Pipeline run not found"})


class RunPipelineTest(MCPTestCase):
    def test_run_pipeline_invalid_config(self):
        result = run_pipeline(
            user=self.USER_ADMIN,
            pipeline_id=str(self.PIPELINE.id),
            config="not json",
        )
        self.assertEqual(result, {"error": "Invalid JSON config string"})

    def test_run_pipeline_invalid_pipeline_id(self):
        result = run_pipeline(
            user=self.USER_ADMIN,
            pipeline_id="00000000-0000-0000-0000-000000000000",
            config="{}",
        )
        self.assertFalse(result["success"])
        self.assertIn("PIPELINE_NOT_FOUND", result["errors"])


class UpdatePipelineTest(MCPTestCase):
    def test_update_pipeline_name(self):
        result = update_pipeline(
            user=self.USER_ADMIN,
            pipeline_id=str(self.PIPELINE.id),
            name="Renamed Pipeline",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["pipeline"]["name"], "Renamed Pipeline")
        self.PIPELINE.refresh_from_db()
        self.assertEqual(self.PIPELINE.name, "Renamed Pipeline")

    def test_update_pipeline_description(self):
        result = update_pipeline(
            user=self.USER_ADMIN,
            pipeline_id=str(self.PIPELINE.id),
            description="New description",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["pipeline"]["description"], "New description")
        self.PIPELINE.refresh_from_db()
        self.assertEqual(self.PIPELINE.description, "New description")

    def test_update_pipeline_schedule(self):
        result = update_pipeline(
            user=self.USER_ADMIN,
            pipeline_id=str(self.PIPELINE.id),
            schedule="0 6 * * 1",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["pipeline"]["schedule"], "0 6 * * 1")
        self.PIPELINE.refresh_from_db()
        self.assertEqual(self.PIPELINE.schedule, "0 6 * * 1")

    def test_update_pipeline_disable_schedule(self):
        update_pipeline(
            user=self.USER_ADMIN,
            pipeline_id=str(self.PIPELINE.id),
            schedule="0 6 * * 1",
        )
        result = update_pipeline(
            user=self.USER_ADMIN,
            pipeline_id=str(self.PIPELINE.id),
            schedule="none",
        )
        self.assertTrue(result["success"])
        self.assertIsNone(result["pipeline"]["schedule"])
        self.PIPELINE.refresh_from_db()
        self.assertIsNone(self.PIPELINE.schedule)

    def test_update_pipeline_no_access(self):
        result = update_pipeline(
            user=self.USER_OUTSIDER,
            pipeline_id=str(self.PIPELINE.id),
            name="Hacked",
        )
        self.assertFalse(result["success"])
        self.assertIn("NOT_FOUND", result["errors"])
