from django.conf import settings
from django.db import models


class Post(models.Model):
    """Publication multi-type : projet, stage, astuce."""

    class PostType(models.TextChoices):
        PROJECT = "project", "Projet"
        INTERNSHIP = "internship", "Stage"
        TIP = "tip", "Astuce"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    post_type = models.CharField(max_length=20, choices=PostType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    code_snippet = models.TextField(blank=True)
    code_language = models.CharField(
        max_length=64,
        blank=True,
        help_text="Langage pour coloration syntaxique (ex: python, javascript).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["post_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.post_type})"

    @property
    def share_url(self):
        return f"/feed/#post-{self.pk}"


class SavedPost(models.Model):
    """Marque-page : utilisateur peut sauvegarder un post."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_posts",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_saved_post",
            ),
        ]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} saved {self.post.title}"


class Story(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stories",
    )
    content = models.CharField(max_length=240, blank=True)
    image = models.ImageField(upload_to="stories/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Story {self.pk} by {self.author.email}"
