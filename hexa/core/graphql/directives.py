from ariadne import SchemaDirectiveVisitor


class AuthNotRequiredDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        field.__auth_not_required = True

        return field
