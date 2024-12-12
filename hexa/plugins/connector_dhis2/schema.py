from ariadne import MutationType, ObjectType, QueryType

from hexa.core.graphql import load_type_defs_from_file

base_type_defs = load_type_defs_from_file(
    "plugins/connector_dhis2/graphql/schema.graphql"
)


query = QueryType()
mutations = MutationType()


instance_object = ObjectType("DHIS2Instance")

data_element_object = ObjectType("DHIS2DataElement")

dhis2_type_defs = [base_type_defs]
dhis2_bindables = [
    query,
    mutations,
    instance_object,
    data_element_object,
]
