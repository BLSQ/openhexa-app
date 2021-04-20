from django_comments.abstracts import CommentAbstractModel

from hexa.common.models import Base


class Comment(Base, CommentAbstractModel):
    pass
