from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, RedirectView, TemplateView
from django.utils import timezone

from apps.users.models import Profile, Follow as FollowModel
from apps.users.forms import (
    EmailAuthenticationForm,
    RegisterForm,
    ProfileUserForm,
    ProfileEditForm,
)
from apps.posts.models import Post, Story
from apps.interactions.models import Share
from core.views import _with_user_flags

User = get_user_model()

class WebLoginView(LoginView):
    template_name = "web/login_pro_final.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

class WebLogoutView(LogoutView):
    next_page = reverse_lazy("home")

class RegisterWebView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("feed")
        return render(request, "web/register_pro.html", {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Compte cree. Bienvenue sur NEXTGEN.")
            return redirect("feed")
        return render(request, "web/register_pro.html", {"form": form})

class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        Profile.objects.get_or_create(user=request.user)
        return render(
            request,
            "web/profile_edit.html",
            {
                "uform": ProfileUserForm(instance=request.user),
                "pform": ProfileEditForm(instance=request.user.profile),
            },
        )

    def post(self, request):
        Profile.objects.get_or_create(user=request.user)
        uform = ProfileUserForm(request.POST, instance=request.user)
        pform = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "Profil mis a jour avec succes.")
            return redirect("profile-detail", pk=request.user.pk)
        return render(request, "web/profile_edit.html", {"uform": uform, "pform": pform})

class AvatarDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        profile = request.user.profile
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save()
            messages.success(request, "Photo de profil supprimee.")
        return redirect("profile-edit")

class MyProfileRedirectView(LoginRequiredMixin, RedirectView):
    pattern_name = "profile-detail"

    def get_redirect_url(self, *args, **kwargs):
        return reverse("profile-detail", kwargs={"pk": self.request.user.pk})

class ProfilePublicView(DetailView):
    model = User
    template_name = "web/profile.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Profile.objects.get_or_create(user=obj)
        return obj

    def get_queryset(self):
        return (
            User.objects.select_related("profile")
            .annotate(
                followers_count=Count("follower_relations", distinct=True),
                following_count=Count("following_relations", distinct=True),
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile_user = self.object
        ctx["posts_list"] = (
            _with_user_flags(Post.objects.filter(author=profile_user), self.request.user)
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
                shares_count=Count("shares", distinct=True),
            )
            .select_related("author", "author__profile")
            .prefetch_related("comments__user__profile")[:30]
        )
        ctx["shared_posts"] = (
            Share.objects.filter(user=profile_user)
            .select_related("post", "post__author", "post__author__profile")
            .prefetch_related("post__comments__user__profile")
            .annotate(
                likes_count=Count("post__likes", distinct=True),
                comments_count=Count("post__comments", distinct=True),
                shares_count=Count("post__shares", distinct=True),
            )[:20]
        )
        ctx["shared_posts_count"] = Share.objects.filter(user=profile_user).count()
        ctx["recent_stories"] = Story.objects.filter(author=profile_user, expires_at__gt=timezone.now())[:6]
        ctx["posts_count"] = profile_user.posts.count()
        ctx["skills_list"] = profile_user.profile.skills or []
        ctx["profile_contacts"] = (
            User.objects.filter(
                Q(follower_relations__follower=profile_user)
                | Q(following_relations__following=profile_user)
            )
            .exclude(pk=profile_user.pk)
            .select_related("profile")
            .distinct()[:10]
        )
        if self.request.user.is_authenticated:
            ctx["i_follow"] = FollowModel.objects.filter(
                follower_id=self.request.user.pk,
                following_id=profile_user.pk,
            ).exists()
        else:
            ctx["i_follow"] = False
        return ctx

class FollowersListView(LoginRequiredMixin, TemplateView):
    template_name = "web/followers_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_id = self.kwargs.get("pk")
        target_user = get_object_or_404(User, pk=user_id)
        list_type = self.request.GET.get("type", "followers")  # "followers" or "following"
        
        if list_type == "following":
            users = User.objects.filter(follower_relations__follower=target_user)
            title = f"Personnes suivies par {target_user.username}"
        else:
            users = User.objects.filter(following_relations__following=target_user)
            title = f"Abonnés de {target_user.username}"

        ctx["target_users"] = users.select_related("profile").annotate(
            followers_count=Count("follower_relations", distinct=True),
        )
        ctx["list_title"] = title
        ctx["profile_user"] = target_user
        return ctx

class FollowToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from django.http import JsonResponse
        target = get_object_or_404(User, pk=pk)
        if target.pk == request.user.pk:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"error": "self-follow"}, status=400)
            messages.warning(request, "Vous ne pouvez pas vous suivre vous-meme.")
            return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))

        relation, created = FollowModel.objects.get_or_create(
            follower=request.user,
            following=target,
        )
        following = True
        if not created:
            relation.delete()
            following = False
        data = {
            "following": following,
            "followers_count": FollowModel.objects.filter(following=target).count(),
        }
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(data)
        return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))
