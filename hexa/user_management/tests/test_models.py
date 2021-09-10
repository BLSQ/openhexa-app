from django import test

from hexa.user_management.models import User, Feature, FeatureFlag


class ModelsTest(test.TestCase):
    def test_initials_no_first_and_last_name(self):
        """Users without first/last names should have the first two letters of their username as initials"""

        user = User(email="plop@openhexa.org")
        self.assertEqual("PL", user.initials)

    def test_initials_with_first_and_last_name(self):
        """Users with a first and last name should have initials composed of the first letter of both names"""

        user = User(email="plop@openhexa.org", first_name="John", last_name="Doe")
        self.assertEqual("JD", user.initials)

    def test_has_feature_flag(self):
        user = User.objects.create_user(
            email="plop@openhexa.org",
            first_name="John",
            last_name="Doe",
            password="ablackcat",
        )
        feature = Feature.objects.create(code="feature_1")
        FeatureFlag.objects.create(user=user, feature=feature)

        self.assertTrue(user.has_feature_flag("feature_1"))
        self.assertFalse(user.has_feature_flag("feature_2"))
