from django.test import SimpleTestCase

from hexa.git.naming import REPO_NAME_MAX_LENGTH, build_repo_name


class BuildRepoNameTest(SimpleTestCase):
    """A repository name is derived from slugs, so it has to stay derivable."""

    def test_a_name_that_fits_is_left_alone(self):
        self.assertEqual("demo-query-monthly-report", build_repo_name("demo-query-monthly-report"))

    def test_a_name_at_the_limit_is_left_alone(self):
        name = "a" * REPO_NAME_MAX_LENGTH

        self.assertEqual(name, build_repo_name(name))

    def test_an_overlong_name_is_cut_to_fit(self):
        self.assertEqual(
            REPO_NAME_MAX_LENGTH, len(build_repo_name("a" * (REPO_NAME_MAX_LENGTH + 1)))
        )

    def test_two_names_cut_at_the_same_point_stay_apart(self):
        # Without this a collision would merge two histories into one repository.
        prefix = "a" * REPO_NAME_MAX_LENGTH

        self.assertNotEqual(build_repo_name(prefix + "one"), build_repo_name(prefix + "two"))

    def test_the_same_name_always_gives_the_same_repository(self):
        name = "a" * 200

        self.assertEqual(build_repo_name(name), build_repo_name(name))
