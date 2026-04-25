from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.interactions.models import Comment, Like
from apps.posts.models import Post
from apps.users.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo users, posts, likes, and comments."

    USERS_DATA = [
        {
            "username": "anas",
            "email": "anas@devconnect.local",
            "first_name": "Anas",
            "bio": "Passionne par Python et les APIs Django.",
        },
        {
            "username": "mohamed",
            "email": "mohamed@devconnect.local",
            "first_name": "Mohamed",
            "bio": "Backend developer, fan de clean architecture.",
        },
        {
            "username": "amin",
            "email": "amin@devconnect.local",
            "first_name": "Amin",
            "bio": "Je partage des astuces code et productivite.",
        },
        {
            "username": "kenza",
            "email": "kenza@devconnect.local",
            "first_name": "Kenza",
            "bio": "Frontend et design system, focus experience utilisateur.",
        },
        {
            "username": "zineb",
            "email": "zineb@devconnect.local",
            "first_name": "Zineb",
            "bio": "Data lover et passionnee par l analyse de donnees.",
        },
        {
            "username": "younes",
            "email": "younes@devconnect.local",
            "first_name": "Younes",
            "bio": "Mobile et web developer, toujours en veille tech.",
        },
    ]

    BASE_POSTS = [
        {
            "author": "anas",
            "title": "API Django pour portfolio dev",
            "description": "J ai termine une API REST avec authentification JWT pour gerer mon portfolio.",
            "post_type": Post.PostType.PROJECT,
        },
        {
            "author": "mohamed",
            "title": "Retour sur mon stage backend",
            "description": "Stage termine avec mise en place de tests et optimisation SQL sur un gros projet.",
            "post_type": Post.PostType.INTERNSHIP,
        },
        {
            "author": "amin",
            "title": "Astuce Python pour lire du JSON",
            "description": "Petit tip: validez toujours vos cles avant acces pour eviter les erreurs KeyError.",
            "post_type": Post.PostType.TIP,
        },
        {
            "author": "kenza",
            "title": "Refonte UI du tableau de bord",
            "description": "J ai redesign la page principale avec une navigation plus claire et moderne.",
            "post_type": Post.PostType.PROJECT,
        },
        {
            "author": "zineb",
            "title": "Mini analyse des donnees utilisateurs",
            "description": "J ai cree un petit dashboard pour suivre engagement, likes et commentaires.",
            "post_type": Post.PostType.PROJECT,
        },
        {
            "author": "younes",
            "title": "Tip Git: commits propres",
            "description": "Decoupez les commits par fonctionnalite pour faciliter la revue et les retours.",
            "post_type": Post.PostType.TIP,
        },
    ]

    COMMENT_TEMPLATES = [
        "Super contenu, merci pour le partage.",
        "Tres propre. J aimerais voir plus de details techniques.",
        "Excellente idee, ca peut aider beaucoup de devs.",
        "Bravo, le resultat est vraiment inspirant.",
        "Top, continue comme ca.",
    ]

    VOLUME_CONFIG = {
        "small": {"posts_per_user": 1, "likes_per_post": 3, "comments_per_post": 2},
        "medium": {"posts_per_user": 2, "likes_per_post": 4, "comments_per_post": 3},
        "large": {"posts_per_user": 3, "likes_per_post": 5, "comments_per_post": 4},
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="Password123!",
            help="Password to assign to all demo users.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo users before seeding.",
        )
        parser.add_argument(
            "--volume",
            choices=tuple(self.VOLUME_CONFIG.keys()),
            default="small",
            help="How much demo data to generate.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        password = options["password"]
        volume = options["volume"]

        if options["reset"]:
            self._reset_demo_users()

        users_by_username = self._upsert_users(password=password)
        posts = self._upsert_posts(users_by_username, volume)
        likes_created, comments_created = self._seed_interactions(posts, users_by_username, volume)

        self.stdout.write(self.style.SUCCESS("Demo seed complete."))
        self.stdout.write(f"Users: {len(users_by_username)}")
        self.stdout.write(f"Posts: {len(posts)}")
        self.stdout.write(f"Likes added: {likes_created}")
        self.stdout.write(f"Comments added: {comments_created}")
        self.stdout.write("Login: email / Password123! (or your --password value)")

    def _reset_demo_users(self):
        usernames = [item["username"] for item in self.USERS_DATA]
        deleted, _ = User.objects.filter(username__in=usernames).delete()
        self.stdout.write(self.style.WARNING(f"Reset enabled: deleted rows count={deleted}"))

    def _upsert_users(self, password):
        users_by_username = {}
        self.stdout.write("Creating or updating demo users...")
        for data in self.USERS_DATA:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                },
            )
            user.email = data["email"]
            user.first_name = data["first_name"]
            user.set_password(password)
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = data["bio"]
            profile.save(update_fields=["bio", "updated_at"])

            users_by_username[data["username"]] = user
            status = "created" if created else "updated"
            self.stdout.write(f" - {data['username']}: {status}")

        return users_by_username

    def _build_posts_data(self, volume):
        cfg = self.VOLUME_CONFIG[volume]
        posts_data = list(self.BASE_POSTS)
        extra_per_user = max(cfg["posts_per_user"] - 1, 0)

        if extra_per_user == 0:
            return posts_data

        post_types = [Post.PostType.PROJECT, Post.PostType.INTERNSHIP, Post.PostType.TIP]
        for item in self.USERS_DATA:
            username = item["username"]
            for idx in range(2, cfg["posts_per_user"] + 1):
                posts_data.append(
                    {
                        "author": username,
                        "title": f"Update {idx} de {username}",
                        "description": (
                            f"{username} partage une nouvelle avancee technique (serie #{idx}). "
                            "Feedback bienvenue."
                        ),
                        "post_type": post_types[(idx - 1) % len(post_types)],
                    }
                )
        return posts_data

    def _upsert_posts(self, users_by_username, volume):
        posts_data = self._build_posts_data(volume)
        posts = []
        self.stdout.write("Creating or updating posts...")

        for item in posts_data:
            author = users_by_username[item["author"]]
            post, created = Post.objects.get_or_create(
                author=author,
                title=item["title"],
                defaults={
                    "description": item["description"],
                    "post_type": item["post_type"],
                },
            )
            if not created:
                post.description = item["description"]
                post.post_type = item["post_type"]
                post.save(update_fields=["description", "post_type", "updated_at"])
            posts.append(post)

        self.stdout.write(f" - total posts processed: {len(posts)}")
        return posts

    def _seed_interactions(self, posts, users_by_username, volume):
        cfg = self.VOLUME_CONFIG[volume]
        ordered_users = [users_by_username[item["username"]] for item in self.USERS_DATA]
        likes_created = 0
        comments_created = 0

        self.stdout.write("Creating likes and comments...")
        for index, post in enumerate(posts):
            candidates = [user for user in ordered_users if user.pk != post.author_id]
            if not candidates:
                continue

            for offset in range(min(cfg["likes_per_post"], len(candidates))):
                liker = candidates[(index + offset) % len(candidates)]
                _, created_like = Like.objects.get_or_create(user=liker, post=post)
                if created_like:
                    likes_created += 1

            for comment_index in range(min(cfg["comments_per_post"], len(candidates))):
                commenter = candidates[(index + comment_index + 1) % len(candidates)]
                template = self.COMMENT_TEMPLATES[comment_index % len(self.COMMENT_TEMPLATES)]
                body = f"{template} [sample {comment_index + 1}]"
                _, created_comment = Comment.objects.get_or_create(
                    user=commenter,
                    post=post,
                    body=body,
                )
                if created_comment:
                    comments_created += 1

        return likes_created, comments_created
