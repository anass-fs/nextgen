from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.posts.models import Post


@receiver(post_save, sender=Post)
def post_activity_score(sender, instance, created, **kwargs):
    # Logique de score désactivée
    pass
