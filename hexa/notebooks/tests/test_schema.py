from hexa.core.test import GraphQLTestCase


class NotebooksTest(GraphQLTestCase):
    def test_notebooks_url(self):
        with self.settings(NOTEBOOKS_URL="http://localhost:8081"):
            r = self.run_query(
                """
                query notebooksUrl {
                    notebooksUrl
                }

                """
            )
            self.assertEqual(
                "http://localhost:8081",
                r["data"]["notebooksUrl"],
            )
