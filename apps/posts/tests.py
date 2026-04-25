from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.posts.models import Post

User = get_user_model()


class PostWebTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="author@test.com",
            username="author",
            password="secret12345",
        )
        self.client.force_login(self.user)

    def test_create_post_from_web_form(self):
        url = reverse("post-create")
        payload = {
            "post_type": Post.PostType.TIP,
            "title": "Astuce Django",
            "description": "Description assez longue pour passer la validation.",
        }
        r = self.client.post(url, payload)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().author_id, self.user.id)

    def test_feed_partial_list_anonymous(self):
        self.client.logout()
        Post.objects.create(
            author=self.user,
            post_type=Post.PostType.PROJECT,
            title="Projet",
            description="Description du projet pour les tests.",
        )
        url = reverse("feed")
        r = self.client.get(url, {"partial": "posts"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Projet")
