from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import BooleanField, Case, Count, Exists, OuterRef, Q, Value, When
from django.utils import timezone

from apps.interactions.models import DirectMessage, Like, Share
from apps.posts.forms import PostForm, StoryForm
from apps.posts.models import Post, SavedPost, Story

User = get_user_model()

PER_PAGE = 8


def _annotated_posts(user):
    posts = (
        Post.objects.select_related("author", "author__profile")
        .prefetch_related("comments__user__profile")
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
            saves_count=Count("saved_by", distinct=True),
            shares_count=Count("shares", distinct=True),
        )
        .order_by("-created_at")
    )
    if user.is_authenticated:
        posts = posts.annotate(
            user_has_liked=Exists(
                Like.objects.filter(post_id=OuterRef("pk"), user_id=user.pk)
            ),
            user_has_saved=Exists(
                SavedPost.objects.filter(post_id=OuterRef("pk"), user_id=user.pk)
            ),
        )
    else:
        posts = posts.annotate(
            user_has_liked=Value(False, output_field=BooleanField()),
            user_has_saved=Value(False, output_field=BooleanField()),
        )
    return posts


def feed_context(request, post_form=None, story_form=None):
    user = request.user
    posts = _annotated_posts(user)
    
    # FILTER BY TYPE
    post_type = request.GET.get("type")
    if post_type in [Post.PostType.PROJECT, Post.PostType.INTERNSHIP, Post.PostType.TIP]:
        posts = posts.filter(post_type=post_type)

    page_num = int(request.GET.get("page") or 1)
    paginator = Paginator(posts, PER_PAGE)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        # Si la page est vide (hors limites), on renvoie une liste vide pour cette page
        from django.core.paginator import Page
        page = Page([], page_num, paginator)
    except PageNotAnInteger:
        page = paginator.page(1)

    following_ids = []
    suggestions = (
        User.objects.exclude(pk=getattr(user, "pk", None))
        .select_related("profile")
        .annotate(
            followers=Count("follower_relations", distinct=True),
            posts_count=Count("posts", distinct=True),
        )
    )
    if user.is_authenticated:
        following_ids = list(
            user.following_relations.values_list("following_id", flat=True)
        )
        suggestions = suggestions.exclude(pk__in=following_ids).order_by("-followers", "-posts_count")[:6]
    else:
        suggestions = suggestions.order_by("-followers", "-posts_count")[:6]

    stories = (
        Story.objects.filter(expires_at__gt=timezone.now())
        .select_related("author", "author__profile")
        .annotate(
            priority=Case(
                When(author_id__in=following_ids, then=Value(0)),
                default=Value(1),
            )
        )
        .order_by("priority", "-created_at")[:12]
    )

    trending_posts = posts.order_by("-likes_count", "-comments_count", "-created_at")[:5]

    return {
        "posts": page,
        "post_form": post_form if post_form is not None else PostForm(),
        "story_form": story_form if story_form is not None else StoryForm(),
        "suggestions": suggestions,
        "stories": stories,
        "trending_posts": trending_posts,
        "following_ids": following_ids,
        "next_page_number": page.next_page_number() if page.has_next() else None,
    }


def conversation_queryset(user):
    thread_messages = (
        DirectMessage.objects.filter(Q(sender=user) | Q(recipient=user))
        .select_related("sender", "sender__profile", "recipient", "recipient__profile")
        .order_by("-created_at")
    )

    conversations = {}
    for message in thread_messages:
        other_user = message.recipient if message.sender_id == user.pk else message.sender
        convo = conversations.get(other_user.pk)

        if convo is None:
            display_name = f"{other_user.first_name} {other_user.last_name}".strip() or other_user.username
            conversations[other_user.pk] = {
                "other_user": other_user,
                "display_name": display_name,
                "last_message": message,
                "unread_count": 0,
            }
            convo = conversations[other_user.pk]

        if message.recipient_id == user.pk and message.read_at is None:
            convo["unread_count"] += 1

    ordered = list(conversations.values())
    ordered.sort(key=lambda item: item["last_message"].created_at, reverse=True)
    return ordered
