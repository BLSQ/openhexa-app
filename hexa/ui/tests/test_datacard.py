from django.http import HttpRequest

from hexa.core.test import TestCase
from hexa.ui.datacard import Action, Datacard, Section, TextProperty
from hexa.ui.datacard.datacard import DatacardOptions
from hexa.ui.datacard.properties import Property
from hexa.user_management.models import User


class MainSection(Section):
    first_name = TextProperty(text="first_name")
    last_name = TextProperty(text="last_name")


class UserDatacard(Datacard):
    title = "email"
    subtitle = "mmh"
    image_src = "bop"
    main = MainSection()
    actions = [
        Action(
            label="Secret action",
            method="GET",
            url="https://notanurl.com",
            enabled_when=lambda r, _: r.user.is_superuser,
            icon="external_link",
        ),
    ]


class DatacardTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JOHN = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            email="john@doe.com",
            password="johnrocks99",
            is_superuser=False,
        )
        cls.USER_JANE = User.objects.create_user(
            first_name="Jane",
            last_name="Doe",
            email="jane@doe.com",
            password="janerocks99",
            is_superuser=True,
        )

    def test_property_registration(self):
        self.assertIsInstance(UserDatacard._meta, DatacardOptions)
        self.assertEqual(1, len(UserDatacard._meta.sections))
        section = UserDatacard._meta.sections["main"]
        self.assertIsInstance(section, Section)
        self.assertEqual(2, len(section.properties))
        for prop in section.properties:
            self.assertIsInstance(prop, Property)

    def test_render(self):
        datacard = UserDatacard(
            self.USER_JOHN,
            request=self.mock_request(self.USER_JOHN),
        )
        rendered_card = str(datacard)
        self.assertGreater(len(rendered_card), 0)
        self.assertIn("John", rendered_card)
        self.assertIn("Doe", rendered_card)
        self.assertIn("john@doe.com", rendered_card)

    def test_render_hidden_action_should_not_display(self):
        request_john = HttpRequest()
        request_john.user = self.USER_JOHN
        request_john.session = {}
        datacard_for_john = UserDatacard(
            self.USER_JOHN,
            request=request_john,
        )
        self.assertNotIn("Secret action", str(datacard_for_john))

    def test_render_hidden_action_should_display(self):
        request_jane = HttpRequest()
        request_jane.user = self.USER_JANE
        request_jane.session = {}
        datacard_for_jane = UserDatacard(
            self.USER_JOHN,
            request=request_jane,
        )
        self.assertIn("Secret action", str(datacard_for_jane))
