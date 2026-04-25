from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View

from apps.interactions.models import Like, Comment, DirectMessage, Share
from apps.interactions.forms import CommentForm, DirectMessageForm
from apps.posts.models import Post
from core.web_context import conversation_queryset

User = get_user_model()


class LikeToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        liked = created
        if not created:
            like.delete()
            liked = False
        count = Like.objects.filter(post=post).count()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"liked": liked, "likes_count": count})
        return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        if not form.is_valid():
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"errors": form.errors}, status=400)
            messages.error(request, "Unable to publish this comment.")
            return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))

        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()

        payload = {
            "comment_html": render_to_string(
                "components/comment_item.html",
                {"comment": comment, "user": request.user},
                request=request,
            ),
            "comments_count": post.comments.count(),
        }
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(payload)
        messages.success(request, "Commentaire publie avec succes.")
        return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))


class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, user=request.user)
        post = comment.post
        comment.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"deleted": True, "comments_count": post.comments.count()})
        messages.success(request, "Commentaire supprime.")
        return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))


class ShareCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        share, created = Share.objects.get_or_create(user=request.user, post=post)
        data = {
            "shared": True,
            "created": created,
            "shares_count": Share.objects.filter(post=post).count(),
        }
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(data)
        messages.success(request, "Publication ajoutee a votre profil.")
        return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))


class ShareDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        share = get_object_or_404(Share, pk=pk, user=request.user)
        share.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"deleted": True})
        messages.success(request, "Partage retire de votre profil.")
        return redirect(request.META.get("HTTP_REFERER") or reverse("feed"))


class RepostCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        original_post = get_object_or_404(
            Post.objects.select_related("author", "author__profile"),
            pk=pk,
        )
        repost = Post(
            author=request.user,
            post_type=original_post.post_type,
            title=(f"Repost: {original_post.title}")[:255],
            description=(
                f"Republished from @{original_post.author.username}\n\n"
                f"{original_post.description}"
            ).strip(),
        )
        if original_post.image:
            repost.image = original_post.image.name
        repost.save()

        payload = {
            "created": True,
            "post_id": repost.pk,
            "redirect_url": reverse("profile-detail", kwargs={"pk": request.user.pk}),
        }
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(payload)
        messages.success(request, "Publication republiee sur votre fil.")
        return redirect("profile-detail", pk=request.user.pk)


class MessageListView(LoginRequiredMixin, View):
    template_name = "web/messages.html"

    def get(self, request):
        selected_user = None
        username = request.GET.get("user", "").strip()
        if username:
            selected_user = get_object_or_404(User.objects.select_related("profile"), username=username)
            if selected_user == request.user:
                selected_user = None
        conversations = conversation_queryset(request.user)

        if request.GET.get("partial") == "conversations":
            return render(request, "components/conversations_list.html", {"conversations": conversations, "selected_user": selected_user})

        thread = []

        if selected_user:
            thread = (
                DirectMessage.objects.filter(
                    Q(sender=request.user, recipient=selected_user)
                    | Q(sender=selected_user, recipient=request.user)
                )
                .select_related("sender", "recipient")
                .order_by("created_at")
            )
            DirectMessage.objects.filter(
                sender=selected_user,
                recipient=request.user,
                read_at__isnull=True,
            ).update(read_at=timezone.now())
        context = {
            "conversations": conversations,
            "selected_user": selected_user,
            "thread": thread,
            "message_form": DirectMessageForm(),
            "message_starters": User.objects.exclude(pk=request.user.pk).select_related("profile")[:8],
        }
        if request.GET.get("partial") == "thread" and selected_user:
            return render(request, "components/message_thread.html", context)
        return render(request, self.template_name, context)

    def post(self, request):
        username = request.POST.get("recipient_username", "").strip()
        recipient = get_object_or_404(User, username=username)
        if recipient == request.user:
            messages.error(request, "You cannot send a message to yourself.")
            return redirect("messages")

        form = DirectMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.recipient = recipient
            msg.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "message_html": render_to_string(
                            "components/message_bubble.html",
                            {"message": msg, "user": request.user},
                            request=request,
                        )
                    }
                )
            messages.success(request, "Message envoye avec succes.")
            return redirect(f"{reverse('messages')}?user={recipient.username}")

        conversations = conversation_queryset(request.user)
        thread = (
            DirectMessage.objects.filter(
                Q(sender=request.user, recipient=recipient)
                | Q(sender=recipient, recipient=request.user)
            )
            .select_related("sender", "recipient")
            .order_by("created_at")
        )
        return render(
            request,
            self.template_name,
            {
                "conversations": conversations,
                "selected_user": recipient,
                "thread": thread,
                "message_form": form,
                "message_starters": User.objects.exclude(pk=request.user.pk).select_related("profile")[:8],
            },
        )
