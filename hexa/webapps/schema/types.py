from ariadne import ObjectType

webapp_permissions = ObjectType("WebappPermissions")

webapp_object = ObjectType("Webapp")

bindables = [
    webapp_permissions,
    webapp_object,
]
