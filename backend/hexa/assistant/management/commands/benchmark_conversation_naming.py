"""Compare naming-agent behaviour across models before changing the default.

A cheaper utility model only saves money if it does not retry more often: each
retry is an extra request, and an exhausted run falls back to a trimmed prompt.
This command runs the real naming agent over a prompt set so retry and fallback
rates can be compared per model.

Every run issues real API calls billed to the organization's provider.
"""

import logging

from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand, CommandError
from pydantic_ai import RunUsage

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.model_builder import AiModelBuilder
from hexa.assistant.models import Conversation
from hexa.user_management.models import AiSettings
from hexa.workspaces.models import Workspace

# Prompts in the shape that motivated the word budget: verbose, French, and
# about a concrete artifact rather than a topic.
_DEFAULT_PROMPTS = [
    "Améliore ce tableau de bord pour que les données soient directement lues à "
    'chaque fois depuis le fichier: "Bundibugyo" / "data" / "analysis" / '
    '"retard_saisie_mve_evenement_v2.csv"',
    "Crée un rapport mensuel de la couverture vaccinale par district de santé "
    "avec les tendances sur les douze derniers mois",
    "Peux-tu analyser les retards de saisie des évènements MVE et me dire "
    "quelles zones de santé sont les plus en retard ?",
    "Add a column with the completeness rate per facility and sort the table by "
    "the worst performing districts first",
]


class _FallbackCounter(logging.Handler):
    """Counts naming fallbacks, which are only reported through the log."""

    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.count = 0

    def emit(self, record):
        if "conversation naming failed" in record.getMessage():
            self.count += 1


class Command(BaseCommand):
    help = "Measure naming-agent retry and fallback rates for a given model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--workspace",
            required=True,
            help="Slug of a workspace whose organization has the AI assistant enabled",
        )
        parser.add_argument(
            "--model",
            choices=AiSettings.Model.values,
            help="Model to name with. Defaults to ASSISTANT_UTILITY_MODEL.",
        )
        parser.add_argument(
            "--prompts",
            help="File with one prompt per line. Defaults to a built-in sample set.",
        )
        parser.add_argument(
            "--repeat",
            type=int,
            default=1,
            help="Times to run each prompt, to see run-to-run variance",
        )

    def handle(self, *args, workspace, model, prompts, repeat, **options):
        try:
            workspace_obj = Workspace.objects.get(slug=workspace)
        except Workspace.DoesNotExist:
            raise CommandError(f"No workspace with slug {workspace!r}")

        prompt_list = self._load_prompts(prompts)

        # Never saved: naming reads the prompt and returns a title, and pricing
        # comes from the built model rather than the conversation.
        conversation = Conversation(workspace=workspace_obj)
        builder = AiModelBuilder.from_conversation(conversation)
        utility_model = builder.build_utility(model)
        agent = BaseAgent(conversation, builder.build(), utility_model)

        logger = logging.getLogger("hexa.assistant.agents.base")
        counter = _FallbackCounter()
        logger.addHandler(counter)
        try:
            self._run(agent, prompt_list, repeat, utility_model, counter)
        finally:
            logger.removeHandler(counter)

    def _load_prompts(self, path: str | None) -> list[str]:
        if not path:
            return _DEFAULT_PROMPTS
        with open(path) as f:
            prompt_list = [line.strip() for line in f if line.strip()]
        if not prompt_list:
            raise CommandError(f"No prompts found in {path!r}")
        return prompt_list

    def _run(self, agent, prompt_list, repeat, utility_model, counter):
        self.stdout.write(f"Naming with {utility_model.api_name}")
        total = retried = input_tokens = output_tokens = 0
        for prompt in prompt_list:
            for _ in range(repeat):
                title, usage = async_to_sync(agent._generate_conversation_name)(prompt)
                requests = usage.requests or 0
                total += 1
                retried += requests > 1
                input_tokens += usage.input_tokens or 0
                output_tokens += usage.output_tokens or 0
                self.stdout.write(f"  [{requests} req] {title}")

        cost = agent._get_cost(
            RunUsage(input_tokens=input_tokens, output_tokens=output_tokens),
            utility_model,
        )
        self.stdout.write(
            f"\n{total} runs: {retried} retried, {counter.count} fell back to a "
            f"trimmed title\ntokens: {input_tokens} in / {output_tokens} out, "
            f"total cost: {cost}"
        )
