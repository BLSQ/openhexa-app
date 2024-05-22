from django.db import models

from hexa.core.models.base import Base

# Create your models here.


class WebPage(Base):
    url = models.URLField()
    title = models.CharField(max_length=255)
    full_width = models.BooleanField(default=False)
    height = models.CharField(null=True, blank=True)
    width = models.CharField(null=True, blank=True)
    allows = models.TextField(default="")
    description = models.TextField(null=True)
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE)

    def __str__(self):
        return self.title
