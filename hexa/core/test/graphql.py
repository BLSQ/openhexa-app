import json

from django import test


class GraphQLTestCase(test.TestCase):
    def run_query(self, query, variables=None):
        return json.loads(
            self.client.post(
                "/graphql/",
                json.dumps(
                    {
                        "operationName": None,
                        "variables": variables if variables is not None else {},
                        "query": query,
                    }
                ),
                content_type="application/json",
            ).content
        )
