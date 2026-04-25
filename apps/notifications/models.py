from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        LIKE = "like", "J'aime"
        COMMENT = "comment", "Commentaire"
        FOLLOW = "follow", "Abonnement"
        SHARE = "share", "Partage"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_actions",
    )
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at", "read"]),
        ]

    def __str__(self):
        return f"{self.notification_type} pour {self.recipient_id}"
