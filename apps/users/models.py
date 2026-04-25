from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Utilisateur avec email comme identifiant principal pour l'API."""

    email = models.EmailField("adresse e-mail", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def __str__(self):
        return self.email


class Profile(models.Model):
    """Profil étendu : bio, compétences, avatar, score d'activité et badge."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(blank=True, max_length=2000)
    skills = models.JSONField(default=list, blank=True)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/%d/", blank=True, null=True)
    activity_score = models.PositiveIntegerField(default=0)
    badge_top_developer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["-activity_score"]),
        ]

    def __str__(self):
        return f"Profil de {self.user.email}"


class Follow(models.Model):
    """Relation follower → following (abonnements confirmés)."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following_relations",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower_relations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_follow_pair",
            ),
        ]
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
        ]

    def __str__(self):
        return f"{self.follower_id} → {self.following_id}"


class FollowRequest(models.Model):
    """Demande de suivi en attente d'acceptation."""

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_DECLINED = "declined"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_ACCEPTED, "Acceptée"),
        (STATUS_DECLINED, "Refusée"),
    ]

    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follow_requests_sent",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follow_requests_received",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["requester", "recipient"],
                name="unique_follow_request_pair",
            ),
        ]
        indexes = [
            models.Index(fields=["recipient", "status"]),
            models.Index(fields=["requester"]),
        ]

    def __str__(self):
        return f"{self.requester.email} → {self.recipient.email} ({self.status})"
