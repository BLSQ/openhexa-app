from django.urls import path

from .views import DatasetRecipeAPIView, TableDataAPIView

app_name = "databases"

urlpatterns = [
    path(
        "api/workspace/<slug:workspace_slug>/database/<str:db_name>/table/<str:table_name>/",
        TableDataAPIView.as_view(),
        name="table_data_api",
    ),
    path(
        "api/workspace/<slug:workspace_slug>/database/<str:db_name>/datasetrecipe/<uuid:recipe_id>/",
        DatasetRecipeAPIView.as_view(),
        name="dataset_recipe_api",
    ),
]
