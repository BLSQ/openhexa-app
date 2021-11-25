from django import test
from django.http import HttpRequest

from hexa.ui.datacard import Datacard, Section, TextProperty
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


class DatacardTest(test.TestCase):
    def test_property_registration(self):
        self.assertIsInstance(UserDatacard._meta, DatacardOptions)
        self.assertEqual(1, len(UserDatacard._meta.sections))
        section = UserDatacard._meta.sections["main"]
        self.assertIsInstance(section, Section)
        self.assertEqual(2, len(section.properties))
        for prop in section.properties:
            self.assertIsInstance(prop, Property)

    def test_render(self):
        user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            email="john@doe.com",
            password="johnrocks99",
        )
        request = HttpRequest()
        request.session = {}
        datacard = UserDatacard(
            user,
            request=request,
        )
        rendered_card = str(datacard)
        self.assertGreater(len(rendered_card), 0)
        self.assertIn("John", rendered_card)
        self.assertIn("Doe", rendered_card)
        self.assertIn("john@doe.com", rendered_card)
