from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from hexa.comments.models import Comment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text", "index"]


def comments(request: HttpRequest) -> HttpResponse:
    form = CommentForm(request.POST, instance=Comment(user=request.user))
    if form.is_valid():
        comment = form.save()
        last = comment.index.comment_set.count() == 1

        return render(
            request,
            "comments/components/comment.html",
            {"comment": comment, "last": last},
        )

    return HttpResponse(status=400, content=form.errors)
