from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.interactions.models import DirectMessage
from apps.notifications.models import Notification

User = get_user_model()


class NotificationWebTests(TestCase):
    def setUp(self):
        self.client = self.client_class()
        self.recipient = User.objects.create_user(
            email="recipient@test.com",
            username="recipient",
            password="secret12345",
        )
        self.actor = User.objects.create_user(
            email="actor@test.com",
            username="actor",
            password="secret12345",
        )

    def test_alerts_count_for_anonymous_user(self):
        response = self.client.get(reverse("alerts-count"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"notifications": 0, "messages": 0})

    def test_alerts_count_for_authenticated_user(self):
        Notification.objects.create(
            recipient=self.recipient,
            actor=self.actor,
            notification_type=Notification.NotificationType.FOLLOW,
        )
        DirectMessage.objects.create(
            sender=self.actor,
            recipient=self.recipient,
            body="Salut",
        )

        self.client.force_login(self.recipient)
        response = self.client.get(reverse("alerts-count"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"notifications": 1, "messages": 1})

    def test_mark_notifications_read_ajax(self):
        Notification.objects.create(
            recipient=self.recipient,
            actor=self.actor,
            notification_type=Notification.NotificationType.FOLLOW,
            read=False,
        )
        Notification.objects.create(
            recipient=self.recipient,
            actor=self.actor,
            notification_type=Notification.NotificationType.LIKE,
            read=False,
        )

        self.client.force_login(self.recipient)
        response = self.client.post(
            reverse("notifications-mark-read"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(
            Notification.objects.filter(recipient=self.recipient, read=False).count(),
            0,
        )
