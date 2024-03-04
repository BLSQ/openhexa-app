from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)

# Create your models here.


class TestMyModel(SoftDeletedModel):
    __test__ = False

    objects = DefaultSoftDeletedManager.from_queryset(SoftDeleteQuerySet)()
    all_objects = IncludeSoftDeletedManager()

    class Meta:
        app_label = "test_abstract_model"
        db_table = "test_my_model"
        managed = False
