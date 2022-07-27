from hexa.catalog.models import Index
from hexa.core.test import TestCase
from hexa.plugins.connector_iaso.models import IASOAccount, IASOPermission
from hexa.user_management.models import Membership, PermissionMode, Team, User


class IASOAccountTest(TestCase):
    USER_JIM = None
    USER_JANE = None
    IASOACC_1 = None
    IASOACC_2 = None
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
        cls.IASOACC_1 = IASOAccount.objects.create(name="iaso-dev1")
        IASOPermission.objects.create(
            team=cls.TEAM, iaso_account=cls.IASOACC_1, mode=PermissionMode.VIEWER
        )
        cls.IASOACC_2 = IASOAccount.objects.create(name="iaso-dev2")

    def test_filter_for_user_regular(self):
        self.assertEqual(
            [self.IASOACC_1],
            list(IASOAccount.objects.filter_for_user(self.USER_JANE)),
        )

    def test_filter_for_user_superuser(self):
        self.assertEqual(
            [self.IASOACC_1, self.IASOACC_2],
            list(IASOAccount.objects.filter_for_user(self.USER_JIM)),
        )

    def test_iasoaccount_delete(self):
        """Deleting a IASOAccount should delete its index as well"""

        iaso_acc = IASOAccount.objects.create(name="iaso-dev")
        iaso_acc_id = iaso_acc.id
        self.assertEqual(1, Index.objects.filter(object_id=iaso_acc_id).count())
        iaso_acc.delete()
        self.assertEqual(0, Index.objects.filter(object_id=iaso_acc_id).count())
