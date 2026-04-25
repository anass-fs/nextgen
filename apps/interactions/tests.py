from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.interactions.models import DirectMessage, Like
from apps.posts.models import Post
from core.web_context import conversation_queryset

User = get_user_model()


class LikeWebTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="u@test.com", username="u", password="p12345678")
        self.other = User.objects.create_user(email="o@test.com", username="o", password="p12345678")
        self.post = Post.objects.create(
            author=self.other,
            post_type=Post.PostType.TIP,
            title="Titre du post",
            description="Description suffisamment longue pour la validation.",
        )
        self.client.force_login(self.user)

    def test_like_post(self):
        url = reverse("post-like", kwargs={"pk": self.post.id})
        r = self.client.post(url)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Like.objects.filter(user=self.user, post=self.post).count(), 1)


class MessageWebTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="me@test.com",
            username="me",
            password="secret12345",
        )
        self.other = User.objects.create_user(
            email="other@test.com",
            username="other",
            password="secret12345",
        )
        self.client.force_login(self.user)

    def test_opening_thread_marks_incoming_messages_as_read(self):
        DirectMessage.objects.create(sender=self.other, recipient=self.user, body="hello 1")
        DirectMessage.objects.create(sender=self.other, recipient=self.user, body="hello 2")

        response = self.client.get(
            reverse("messages"),
            {"user": self.other.username, "partial": "thread"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            DirectMessage.objects.filter(
                sender=self.other,
                recipient=self.user,
                read_at__isnull=True,
            ).count(),
            0,
        )

    def test_conversation_queryset_aggregates_unread_and_last_message(self):
        DirectMessage.objects.create(sender=self.other, recipient=self.user, body="first")
        DirectMessage.objects.create(sender=self.other, recipient=self.user, body="second")
        DirectMessage.objects.create(sender=self.user, recipient=self.other, body="reply")

        conversations = conversation_queryset(self.user)

        self.assertEqual(len(conversations), 1)
        convo = conversations[0]
        self.assertEqual(convo["other_user"].pk, self.other.pk)
        self.assertEqual(convo["unread_count"], 2)
        self.assertEqual(convo["last_message"].body, "reply")
