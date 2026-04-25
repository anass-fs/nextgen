from django.contrib import admin

from apps.interactions.models import Comment, Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    raw_id_fields = ("user", "post")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    raw_id_fields = ("user", "post")
