from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import AccessmodProfile
from hexa.user_management.models import User


class MeTest(GraphQLTestCase):
    USER_SABRINA = None
    USER_REBECCA = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        AccessmodProfile.objects.create(
            user=cls.USER_SABRINA, is_accessmod_superuser=True
        )
        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )
