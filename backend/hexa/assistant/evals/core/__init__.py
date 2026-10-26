"""Machinery shared by every suite.

Nothing here knows which agent is under test. Anything that does belongs in the
suite package instead.
"""

# The actual cost of the run (as the app billed it), recorded by each suite's task.
# Used instead of pydantic-evals a `cost` metric from the model request spans,
# to make sure we take into account price overrides if any are set.
CONVERSATION_COST_METRIC = "conversation_cost"
