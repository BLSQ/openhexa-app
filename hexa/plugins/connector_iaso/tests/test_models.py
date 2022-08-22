from hexa.catalog.models import Index
from hexa.core.test import TestCase
from hexa.plugins.connector_iaso.models import Account, IASOPermission
from hexa.user_management.models import Membership, PermissionMode, Team, User


class AccountTest(TestCase):
    USER_JIM = None
    USER_JANE = None
    ACC_1 = None
    ACC_2 = None
    TEAM = None

    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_JIM = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimmytyjim",
            is_superuser=True,
        )
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janityjane",
            is_superuser=False,
        )
        Membership.objects.create(team=cls.TEAM, user=cls.USER_JANE)
        cls.ACC_1 = Account.objects.create(name="iaso-dev1")
        IASOPermission.objects.create(
            team=cls.TEAM, iaso_account=cls.ACC_1, mode=PermissionMode.VIEWER
        )
        cls.ACC_2 = Account.objects.create(name="iaso-dev2")

    def test_filter_for_user_regular(self):
        self.assertEqual(
            [self.ACC_1],
            list(Account.objects.filter_for_user(self.USER_JANE)),
        )

    def test_filter_for_user_superuser(self):
        self.assertEqual(
            [self.ACC_1, self.ACC_2],
            list(Account.objects.filter_for_user(self.USER_JIM)),
        )

    def test_account_delete(self):
        """Deleting a Account should delete its index as well"""

        account = Account.objects.create(name="iaso-dev")
        self.assertEqual(1, Index.objects.filter(object_id=account.id).count())
        account.delete()
        self.assertEqual(0, Index.objects.filter(object_id=account.id).count())
