from django_comments.abstracts import CommentAbstractModel

from hexa.core.models import Base


class Comment(Base, CommentAbstractModel):
    pass
