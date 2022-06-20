from ariadne_django.views import GraphQLView
from django.contrib.auth.mixins import LoginRequiredMixin


class SecureGraphQLView(GraphQLView, LoginRequiredMixin):
    pass
