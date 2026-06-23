import base64

from django.db import models

from hexa.core.models.base import Base


class FailedEmail(Base):
    """A best-effort email that failed to send.

    Stores the fully rendered message so it can be resent as-is from the Django
    admin without re-rendering templates (whose variables may not be JSON
    serializable).
    """

    subject = models.TextField()
    recipients = models.JSONField(default=list)
    text_body = models.TextField()
    html_body = models.TextField(blank=True, default="")
    attachments = models.JSONField(default=list)
    error_message = models.TextField(blank=True, default="")
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "core_failed_email"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.subject} -> {', '.join(self.recipients)}"

    def decoded_attachments(self):
        return [
            (a["filename"], base64.b64decode(a["content"]), a["mimetype"])
            for a in self.attachments
        ]
