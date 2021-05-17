from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render

from hexa.comments.models import Comment


def comments(request):
    content_type = ContentType.objects.get_by_natural_key(
        *request.POST["content_type_key"].split(".")
    )
    target_object = content_type.get_object_for_this_type(id=request.POST["object_id"])
    comment = Comment.objects.create(
        user=request.user,
        text=request.POST["text"],
        content_type=content_type,
        object=target_object,
    )
    last = target_object.comments.count() == 1

    return render(
        request,
        "comments/components/comment.html",
        {"comment": comment, "last": last},
    )
