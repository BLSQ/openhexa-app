import io
import zipfile
from datetime import timedelta

from django.utils import timezone
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.edit_pipeline_agent import EditPipelineAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.assistant.tools.pipelines import get_pipeline_run
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineVersion,
)
from hexa.pipelines.utils import SECRET_MASK
from hexa.user_management.models import User

from ._helpers import FakeModelBuilder, _make_tool_call_model, _make_zipfile, run_agent
from ._testcase import AgentTestCase


def _make_run(user, pipeline, version, state, execution_date, **fields):
    return PipelineRun.objects.create(
        pipeline=pipeline,
        pipeline_version=version,
        user=user,
        run_id=f"run-{execution_date.isoformat()}",
        execution_date=execution_date,
        trigger_mode=PipelineRunTrigger.MANUAL,
        state=state,
        **fields,
    )


class EditPipelineAgentExtraInstructionsTest(AgentTestCase):
    def _make_agent(self, pipeline=None, user=None):
        conversation = Conversation(
            user=user or self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )
        if pipeline is not None:
            conversation.linked_object = pipeline
        conversation.save()
        return EditPipelineAgent(conversation, FakeModelBuilder(TestModel()))

    def test_no_pipeline_returns_empty_string(self):
        agent = self._make_agent(pipeline=None)
        self.assertEqual(agent._extra_instructions(), "")

    def test_pipeline_without_version_includes_name_and_code(self):
        pipeline = Pipeline.objects.create(
            code="my-pipeline", name="My Pipeline", workspace=self.workspace
        )
        agent = self._make_agent(pipeline=pipeline)
        instructions = agent._extra_instructions()
        self.assertIn("My Pipeline", instructions)
        self.assertIn("my-pipeline", instructions)

    def test_pipeline_description_is_included(self):
        pipeline = Pipeline.objects.create(
            code="desc-pipeline",
            name="Described Pipeline",
            description="Loads data from S3.",
            workspace=self.workspace,
        )
        agent = self._make_agent(pipeline=pipeline)
        self.assertIn("Loads data from S3.", agent._extra_instructions())

    def test_pipeline_without_description_omits_description_line(self):
        pipeline = Pipeline.objects.create(
            code="nodesc-pipeline",
            name="No Description",
            description="",
            workspace=self.workspace,
        )
        agent = self._make_agent(pipeline=pipeline)
        self.assertNotIn("Description:", agent._extra_instructions())

    def test_pipeline_with_version_includes_version_name(self):
        pipeline = Pipeline.objects.create(
            code="versioned-pipeline", name="Versioned", workspace=self.workspace
        )
        PipelineVersion.objects.create(
            pipeline=pipeline, user=self.user, name="Initial release"
        )
        agent = self._make_agent(pipeline=pipeline)
        self.assertIn("Initial release", agent._extra_instructions())

    def test_pipeline_with_zipfile_includes_file_contents(self):
        pipeline = Pipeline.objects.create(
            code="zip-pipeline", name="Zip Pipeline", workspace=self.workspace
        )
        PipelineVersion.objects.create(
            pipeline=pipeline,
            user=self.user,
            zipfile=_make_zipfile(("pipeline.py", "print('hello')")),
        )
        agent = self._make_agent(pipeline=pipeline)
        instructions = agent._extra_instructions()
        self.assertIn("pipeline.py", instructions)
        self.assertIn("print('hello')", instructions)

    def test_pipeline_with_multiple_files_includes_all(self):
        pipeline = Pipeline.objects.create(
            code="multi-pipeline", name="Multi File", workspace=self.workspace
        )
        PipelineVersion.objects.create(
            pipeline=pipeline,
            user=self.user,
            zipfile=_make_zipfile(
                ("pipeline.py", "# main"),
                ("utils.py", "# helpers"),
            ),
        )
        agent = self._make_agent(pipeline=pipeline)
        instructions = agent._extra_instructions()
        self.assertIn("pipeline.py", instructions)
        self.assertIn("utils.py", instructions)

    def test_binary_file_is_listed_so_it_can_be_deleted(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("pipeline.py", "# main")
            zf.writestr("assets/logo.png", b"\x00\xff\xfe")
        pipeline = Pipeline.objects.create(
            code="binary-pipeline", name="Binary Pipeline", workspace=self.workspace
        )
        PipelineVersion.objects.create(
            pipeline=pipeline, user=self.user, zipfile=buf.getvalue()
        )
        agent = self._make_agent(pipeline=pipeline)
        instructions = agent._extra_instructions()
        self.assertIn("assets/logo.png", instructions)
        self.assertIn("(binary)", instructions)

    def test_pending_deletions_are_listed(self):
        pipeline = Pipeline.objects.create(
            code="pending-del", name="Pending Del", workspace=self.workspace
        )
        PipelineVersion.objects.create(
            pipeline=pipeline, user=self.user, zipfile=_make_zipfile(("a.py", "# a"))
        )
        agent = self._make_agent(pipeline=pipeline)
        message = Message.objects.create(
            conversation=agent.conversation,
            role=Message.Role.ASSISTANT,
            content=[],
        )
        ToolInvocation.objects.create(
            message=message,
            tool_name="propose_pipeline_version",
            tool_call_id="call-pending-del",
            tool_input={},
            success=True,
            proposal_pending=True,
            tool_output={
                "files": [{"name": "a.py", "content": "# a"}],
                "deleted_paths": ["assets/logo.png"],
            },
        )
        instructions = agent._extra_instructions()
        self.assertIn("Staged For Deletion", instructions)
        self.assertIn("assets/logo.png", instructions)

    def _make_run(self, pipeline, version, state, execution_date, **fields):
        return _make_run(self.user, pipeline, version, state, execution_date, **fields)

    def _run_line(self, instructions, run):
        return next(line for line in instructions.splitlines() if str(run.id) in line)

    def test_recent_runs_show_parameters_and_last_log_line_of_failed_runs(self):
        pipeline = Pipeline.objects.create(
            code="crashing", name="Crashing", workspace=self.workspace
        )
        version = PipelineVersion.objects.create(pipeline=pipeline, user=self.user)
        run = self._make_run(
            pipeline,
            version,
            PipelineRunState.FAILED,
            timezone.now(),
            config={"mode": "crash"},
            run_logs="Traceback (most recent call last):\n  ...\nKeyError: 'population'\n",
        )
        line = self._run_line(self._make_agent(pipeline)._extra_instructions(), run)
        self.assertIn('{"mode": "crash"}', line)
        self.assertIn("KeyError: 'population'", line)

    def test_recent_runs_prefer_error_message_over_logs(self):
        pipeline = Pipeline.objects.create(
            code="reported", name="Reported", workspace=self.workspace
        )
        run = self._make_run(
            pipeline,
            None,
            PipelineRunState.FAILED,
            timezone.now(),
            messages=[
                {"priority": "INFO", "message": "Starting"},
                {"priority": "ERROR", "message": "DHIS2 returned 401"},
            ],
            run_logs="SystemExit: 1",
        )
        line = self._run_line(self._make_agent(pipeline)._extra_instructions(), run)
        self.assertIn("DHIS2 returned 401", line)
        self.assertNotIn("SystemExit", line)

    def test_recent_runs_omit_error_for_successful_runs(self):
        pipeline = Pipeline.objects.create(
            code="fine", name="Fine", workspace=self.workspace
        )
        run = self._make_run(
            pipeline,
            None,
            PipelineRunState.SUCCESS,
            timezone.now(),
            run_logs="Pipeline completed.",
        )
        line = self._run_line(self._make_agent(pipeline)._extra_instructions(), run)
        self.assertNotIn("error", line)

    def test_recent_runs_mask_secret_parameters(self):
        pipeline = Pipeline.objects.create(
            code="secretive", name="Secretive", workspace=self.workspace
        )
        version = PipelineVersion.objects.create(
            pipeline=pipeline,
            user=self.user,
            parameters=[
                {"code": "token", "type": "secret"},
                {"code": "country", "type": "str"},
            ],
        )
        run = self._make_run(
            pipeline,
            version,
            PipelineRunState.SUCCESS,
            timezone.now(),
            config={"token": "s3cr3t", "country": "BE"},
        )
        line = self._run_line(self._make_agent(pipeline)._extra_instructions(), run)
        self.assertNotIn("s3cr3t", line)
        self.assertIn(SECRET_MASK, line)
        self.assertIn('"country": "BE"', line)

    def test_recent_runs_clip_long_errors(self):
        pipeline = Pipeline.objects.create(
            code="verbose", name="Verbose", workspace=self.workspace
        )
        run = self._make_run(
            pipeline,
            None,
            PipelineRunState.FAILED,
            timezone.now(),
            run_logs="ValueError: " + "x" * 5000,
        )
        line = self._run_line(self._make_agent(pipeline)._extra_instructions(), run)
        self.assertLess(len(line), 600)
        self.assertIn("…", line)

    def test_pipeline_without_runs_omits_recent_runs(self):
        pipeline = Pipeline.objects.create(
            code="no-runs", name="No Runs", workspace=self.workspace
        )
        PipelineVersion.objects.create(pipeline=pipeline, user=self.user)
        agent = self._make_agent(pipeline=pipeline)
        self.assertNotIn("Recent Runs", agent._extra_instructions())

    def test_recent_runs_hidden_from_users_without_access(self):
        pipeline = Pipeline.objects.create(
            code="private", name="Private", workspace=self.workspace
        )
        run = self._make_run(pipeline, None, PipelineRunState.FAILED, timezone.now())
        outsider = User.objects.create_user("outsider@example.com", "password")
        instructions = self._make_agent(pipeline, user=outsider)._extra_instructions()
        self.assertNotIn("Recent Runs", instructions)
        self.assertNotIn(str(run.id), instructions)

    def test_recent_runs_lists_latest_five_most_recent_first(self):
        pipeline = Pipeline.objects.create(
            code="with-runs", name="With Runs", workspace=self.workspace
        )
        version = PipelineVersion.objects.create(
            pipeline=pipeline, user=self.user, name="Release"
        )
        now = timezone.now()
        runs = [
            self._make_run(
                pipeline,
                version,
                PipelineRunState.FAILED if i == 0 else PipelineRunState.SUCCESS,
                now - timedelta(hours=i),
            )
            for i in range(6)
        ]
        agent = self._make_agent(pipeline=pipeline)
        instructions = agent._extra_instructions()

        self.assertIn("Recent Runs", instructions)
        self.assertNotIn(str(runs[5].id), instructions)
        positions = [instructions.index(str(run.id)) for run in runs[:5]]
        self.assertEqual(positions, sorted(positions))
        newest_line = next(
            line for line in instructions.splitlines() if str(runs[0].id) in line
        )
        self.assertIn(PipelineRunState.FAILED, newest_line)
        self.assertIn(runs[0].execution_date.isoformat(), newest_line)
        self.assertIn(version.version_name, newest_line)
        self.assertIn("5 most recent only", instructions)

    def test_recent_runs_exclude_other_pipelines(self):
        pipeline = Pipeline.objects.create(
            code="mine", name="Mine", workspace=self.workspace
        )
        other = Pipeline.objects.create(
            code="other", name="Other", workspace=self.workspace
        )
        other_run = self._make_run(other, None, PipelineRunState.FAILED, timezone.now())
        agent = self._make_agent(pipeline=pipeline)
        instructions = agent._extra_instructions()
        self.assertNotIn(str(other_run.id), instructions)
        self.assertNotIn("Recent Runs", instructions)

    def test_get_pipeline_run_tool_is_available(self):
        self.assertIn(get_pipeline_run, EditPipelineAgent.tools)

    def test_pipeline_is_injected_into_context(self):
        pipeline = Pipeline.objects.create(
            code="ctx-pipeline", name="Context Pipeline", workspace=self.workspace
        )
        agent = self._make_agent(pipeline=pipeline)
        self.assertIn("pipeline", agent._context)
        self.assertEqual(agent._context["pipeline"], pipeline)

    def test_no_pipeline_context_pipeline_is_none(self):
        agent = self._make_agent(pipeline=None)
        self.assertIn("pipeline", agent._context)
        self.assertIsNone(agent._context["pipeline"])


class EditPipelineAgentToolCallTest(AgentTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.pipeline = Pipeline.objects.create(
            code="tool-pipeline", name="Tool Pipeline", workspace=cls.workspace
        )

    def test_propose_pipeline_version_call_is_persisted(self):
        files_arg = [{"name": "pipeline.py", "content": "print('v2')"}]
        model = _make_tool_call_model(
            "propose_pipeline_version", {"modified_files": files_arg}
        )
        conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )
        conversation.linked_object = self.pipeline
        conversation.save()
        agent = EditPipelineAgent(conversation, FakeModelBuilder(model))
        run_agent(agent, "Update the pipeline")
        invocation = self.first_tool_invocation(conversation)
        self.assertEqual(invocation.tool_name, "propose_pipeline_version")
        self.assertTrue(invocation.success)
        self.assertIn("files", invocation.tool_output)
        self.assertEqual(invocation.tool_output["files"][0]["name"], "pipeline.py")

    def test_propose_pipeline_version_is_marked_pending(self):
        model = _make_tool_call_model(
            "propose_pipeline_version",
            {"modified_files": [{"name": "pipeline.py", "content": "print('v2')"}]},
        )
        conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )
        conversation.linked_object = self.pipeline
        conversation.save()
        agent = EditPipelineAgent(conversation, FakeModelBuilder(model))
        run_agent(agent, "Update the pipeline")
        invocation = self.first_tool_invocation(conversation)
        self.assertTrue(invocation.proposal_pending)

    def test_new_proposal_supersedes_previous_pending_one(self):
        conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )
        conversation.linked_object = self.pipeline
        conversation.save()

        first_model = _make_tool_call_model(
            "propose_pipeline_version",
            {"modified_files": [{"name": "pipeline.py", "content": "print('v2')"}]},
        )
        run_agent(
            EditPipelineAgent(conversation, FakeModelBuilder(first_model)),
            "First change",
        )

        second_model = _make_tool_call_model(
            "propose_pipeline_version",
            {"modified_files": [{"name": "pipeline.py", "content": "print('v3')"}]},
        )
        run_agent(
            EditPipelineAgent(conversation, FakeModelBuilder(second_model)),
            "Second change",
        )

        invocations = list(
            ToolInvocation.objects.filter(
                message__conversation=conversation,
                tool_name="propose_pipeline_version",
            ).order_by("created_at")
        )
        self.assertEqual(len(invocations), 2)
        self.assertFalse(invocations[0].proposal_pending)
        self.assertTrue(invocations[1].proposal_pending)


class GetPipelineRunToolTest(AgentTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.pipeline = Pipeline.objects.create(
            code="linked", name="Linked", workspace=cls.workspace
        )
        cls.version = PipelineVersion.objects.create(
            pipeline=cls.pipeline,
            user=cls.user,
            parameters=[{"code": "token", "type": "secret"}],
        )
        cls.linked_run = _make_run(
            cls.user,
            cls.pipeline,
            cls.version,
            PipelineRunState.FAILED,
            timezone.now(),
            config={"token": "s3cr3t", "mode": "crash"},
            run_logs="\n".join(f"line {i}" for i in range(1, 301)),
        )
        cls.other_pipeline = Pipeline.objects.create(
            code="other", name="Other", workspace=cls.workspace
        )
        cls.other_run = _make_run(
            cls.user,
            cls.other_pipeline,
            None,
            PipelineRunState.FAILED,
            timezone.now(),
        )

    def test_reads_run_of_linked_pipeline_with_secrets_masked(self):
        result = get_pipeline_run(
            user=self.user, pipeline=self.pipeline, run_id=str(self.linked_run.id)
        )
        self.assertEqual(str(result["id"]), str(self.linked_run.id))
        self.assertEqual(result["config"], {"token": SECRET_MASK, "mode": "crash"})
        self.assertIn("logsTruncated", result)

    def test_rejects_run_of_another_pipeline(self):
        result = get_pipeline_run(
            user=self.user, pipeline=self.pipeline, run_id=str(self.other_run.id)
        )
        self.assertEqual(
            result, {"error": "No run with this id belongs to the current pipeline"}
        )

    def test_rejects_without_linked_pipeline(self):
        result = get_pipeline_run(
            user=self.user, pipeline=None, run_id=str(self.linked_run.id)
        )
        self.assertIn("error", result)

    def test_rejects_invalid_run_id(self):
        result = get_pipeline_run(user=self.user, pipeline=self.pipeline, run_id="#2")
        self.assertEqual(result, {"error": "'#2' is not a valid run id"})
