from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.models import Notification
from apps.users.models import Follow, Profile, User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Follow)
def notify_on_follow(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.following_id == instance.follower_id:
        return
    Notification.objects.create(
        recipient_id=instance.following_id,
        actor_id=instance.follower_id,
        notification_type=Notification.NotificationType.FOLLOW,
        post=None,
    )
