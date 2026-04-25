from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from apps.posts.models import Post, SavedPost, Story
from apps.posts.forms import PostForm, StoryForm
from core.views import _with_user_flags
from core.web_context import feed_context

User = get_user_model()


class FeedView(View):
    def get(self, request):
        context = feed_context(request)
        if request.GET.get("partial") == "posts":
            return render(request, "components/feed_posts.html", context)
        return render(request, "web/feed.html", context)


class PostCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        story_form = StoryForm()
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Publication publiee avec succes.")
            return redirect("feed")
        return render(request, "web/feed.html", feed_context(request, form, story_form))


class StoryCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = StoryForm(request.POST, request.FILES)
        post_form = PostForm()
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            messages.success(request, "Story publiee pour 24 heures.")
            return redirect("feed")
        return render(request, "web/feed.html", feed_context(request, post_form, form))


class SavePostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        saved, created = SavedPost.objects.get_or_create(user=request.user, post=post)
        is_saved = True
        if not created and request.GET.get("toggle") == "1":
            saved.delete()
            is_saved = False
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "saved": is_saved,
                    "saves_count": SavedPost.objects.filter(post=post).count(),
                }
            )
        messages.success(request, "Post sauvegarde." if is_saved else "Post retire des sauvegardes.")
        return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))


class UnsavePostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        SavedPost.objects.filter(user=request.user, post=post).delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"saved": False, "saves_count": SavedPost.objects.filter(post=post).count()})
        messages.success(request, "Post retire des sauvegardes.")
        return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))


class PostDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, author=request.user)
        post.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"deleted": True})
        messages.success(request, "Publication supprimee.")
        return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))


class StoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        story = get_object_or_404(Story, pk=pk, author=request.user)
        story.delete()
        messages.success(request, "Story supprimee.")
        return redirect("feed")


class SavedPostsListView(LoginRequiredMixin, TemplateView):
    template_name = "web/saved_posts.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        saved = (
            SavedPost.objects.filter(user=self.request.user)
            .select_related("post", "post__author", "post__author__profile")
            .prefetch_related("post__comments__user__profile")
            .annotate(
                likes_count=Count("post__likes", distinct=True),
                comments_count=Count("post__comments", distinct=True),
            )
        )
        post_ids = [item.post_id for item in saved]
        posts = _with_user_flags(
            Post.objects.filter(pk__in=post_ids)
            .select_related("author", "author__profile")
            .prefetch_related("comments__user__profile")
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
                saves_count=Count("saved_by", distinct=True),
            ),
            self.request.user,
        )
        post_map = {post.pk: post for post in posts}
        ctx["saved_posts"] = [post_map[item.post_id] for item in saved if item.post_id in post_map]
        ctx["saved_posts_count"] = len(ctx["saved_posts"])
        return ctx
