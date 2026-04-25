from apps.notifications.models import Notification
from apps.interactions.models import DirectMessage

def unread_counts(request):
    if not request.user.is_authenticated:
        return {}
    
    return {
        'unread_notifications_count': Notification.objects.filter(recipient=request.user, read=False).count(),
        'unread_messages_count': DirectMessage.objects.filter(recipient=request.user, read_at__isnull=True).count(),
    }
