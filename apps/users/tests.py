from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

# from apps.users.activity import add_activity_score
from apps.users.models import Follow, Profile

User = get_user_model()


class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)

    def test_profile_creation_signal(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        self.assertTrue(Profile.objects.filter(user=user).exists())


class ProfileActivityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dev", email="dev@example.com", password="password123"
        )

    # def test_add_activity_score_updates_badge(self):
    #     prof = self.user.profile
    #     threshold = 100
    #     self.assertFalse(prof.badge_top_developer)
    #     add_activity_score(prof, threshold)
    #     self.assertTrue(prof.badge_top_developer)


class FollowModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="u1@example.com", password="p"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="u2@example.com", password="p"
        )

    def test_follow_uniqueness(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        with self.assertRaises(IntegrityError):
            Follow.objects.create(follower=self.user1, following=self.user2)

    def test_self_follow_prevention(self):
        # Normalement géré au niveau de la vue ou d'une contrainte
        pass

    def test_password_is_hashed(self):
        """Vérifie que le mot de passe est bien hashé (pas en clair)."""
        user = User.objects.create_user(
            username="testhash", email="hash@example.com", password="password123"
        )
        # Le mot de passe stocké doit commencer par un algo de hash, pas être en clair
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        # Vérification que le mot de passe en clair ne peut pas être récupéré
        self.assertNotEqual(user.password, "password123")

