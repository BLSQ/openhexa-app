from decimal import Decimal

from django.test import SimpleTestCase

from hexa.assistant.admin import format_conversation_cost, format_message_cost
from hexa.assistant.models import Conversation, Message


class MessageCostDisplayTest(SimpleTestCase):
    """An assistant message ran on a model, so a missing cost means the model
    could not be priced, which the budget silently misses; the admin must not.
    """

    def _message(self, cost, input_tokens=120) -> Message:
        return Message(
            role=Message.Role.ASSISTANT, input_tokens=input_tokens, cost=cost
        )

    def test_a_priced_message_shows_its_cost(self):
        self.assertEqual(
            format_message_cost(self._message(Decimal("0.1734"))), "$0.1734"
        )

    def test_an_unpriced_message_is_flagged(self):
        self.assertIn("unpriced", format_message_cost(self._message(None)))

    def test_a_zero_cost_message_is_flagged_too(self):
        self.assertIn("unpriced", format_message_cost(self._message(Decimal(0))))

    def test_a_user_message_has_nothing_to_price(self):
        message = Message(role=Message.Role.USER, input_tokens=None, cost=None)
        self.assertEqual(format_message_cost(message), "—")


class ConversationCostDisplayTest(SimpleTestCase):
    def _conversation(self, unpriced: int) -> Conversation:
        conversation = Conversation(cost=Decimal("0.000168"))
        conversation.unpriced_messages = unpriced
        return conversation

    def test_a_fully_priced_conversation_shows_its_cost_alone(self):
        self.assertEqual(format_conversation_cost(self._conversation(0)), "$0.0002")

    def test_unpriced_messages_are_counted_next_to_the_cost(self):
        text = format_conversation_cost(self._conversation(2))
        self.assertIn("$0.0002", text)
        self.assertIn("2 unpriced", text)
