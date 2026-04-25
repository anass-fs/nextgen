from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Count, Exists, OuterRef, Q, Value
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from apps.interactions.models import DirectMessage, Like
from apps.notifications.models import Notification
from apps.posts.models import Post, SavedPost

User = get_user_model()

def _with_user_flags(queryset, user):
    """Utilitaire pour annoter si l'utilisateur a aimé ou sauvegardé un post."""
    if user.is_authenticated:
        return queryset.annotate(
            user_has_liked=Exists(
                Like.objects.filter(post_id=OuterRef("pk"), user_id=user.pk)
            ),
            user_has_saved=Exists(
                SavedPost.objects.filter(post_id=OuterRef("pk"), user_id=user.pk)
            ),
        )
    return queryset.annotate(
        user_has_liked=Value(False, output_field=BooleanField()),
        user_has_saved=Value(False, output_field=BooleanField()),
    )

class AlertsCountView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"notifications": 0, "messages": 0})
        return JsonResponse({
            "notifications": Notification.objects.filter(recipient=request.user, read=False).count(),
            "messages": DirectMessage.objects.filter(recipient=request.user, read_at__isnull=True).count(),
        })

class HomeView(View):
    def get(self, request):
        return redirect("landing")

class LandingView(TemplateView):
    template_name = "web/landing.html"

class SearchView(TemplateView):
    template_name = "web/search.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        ctx["query"] = query
        if query:
            users = (
                User.objects.filter(
                    Q(username__icontains=query)
                    | Q(email__icontains=query)
                    | Q(first_name__icontains=query)
                    | Q(last_name__icontains=query)
                    | Q(profile__bio__icontains=query)
                )
                .select_related("profile")
                .annotate(
                    followers_count=Count("follower_relations", distinct=True),
                    following_count=Count("following_relations", distinct=True),
                )[:20]
            )
            posts = _with_user_flags((
                Post.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
                .select_related("author", "author__profile")
                .prefetch_related("comments__user__profile")
                .annotate(
                    likes_count=Count("likes", distinct=True),
                    comments_count=Count("comments", distinct=True),
                    saves_count=Count("saved_by", distinct=True),
                )[:20]
            ), self.request.user)
        else:
            users = []
            posts = []
        ctx["users"] = users
        ctx["posts"] = posts
        return ctx
