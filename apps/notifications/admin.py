from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "actor", "notification_type", "read", "created_at")
    list_filter = ("notification_type", "read")
    raw_id_fields = ("recipient", "actor", "post")
