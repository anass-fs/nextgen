from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.interactions.models import Comment, Like, Share
from apps.notifications.models import Notification


@receiver(post_save, sender=Like)
def like_notify_and_score(sender, instance, created, **kwargs):
    if not created:
        return
    post = instance.post
    if post.author_id == instance.user_id:
        return
    Notification.objects.create(
        recipient_id=post.author_id,
        actor_id=instance.user_id,
        notification_type=Notification.NotificationType.LIKE,
        post_id=post.id,
    )


@receiver(post_save, sender=Share)
def share_notify_and_score(sender, instance, created, **kwargs):
    if not created:
        return
    post = instance.post
    if post.author_id == instance.user_id:
        return
    Notification.objects.create(
        recipient_id=post.author_id,
        actor_id=instance.user_id,
        notification_type=Notification.NotificationType.SHARE,
        post_id=post.id,
    )


@receiver(post_save, sender=Comment)
def comment_notify_and_score(sender, instance, created, **kwargs):
    if not created:
        return
    post = instance.post
    if post.author_id != instance.user_id:
        Notification.objects.create(
            recipient_id=post.author_id,
            actor_id=instance.user_id,
            notification_type=Notification.NotificationType.COMMENT,
            post_id=post.id,
        )
