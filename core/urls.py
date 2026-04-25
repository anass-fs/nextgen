from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from apps.posts.views import (
    FeedView, PostCreateView, StoryCreateView, PostDeleteView, 
    StoryDeleteView, SavePostView, UnsavePostView, SavedPostsListView
)
from apps.users.views import (
    WebLoginView, WebLogoutView, RegisterWebView, ProfileEditView, 
    AvatarDeleteView, MyProfileRedirectView, ProfilePublicView, 
    FollowersListView, FollowToggleView
)
from apps.interactions.views import (
    LikeToggleView, CommentCreateView, CommentDeleteView, 
    ShareCreateView, ShareDeleteView, RepostCreateView, MessageListView
)
from apps.notifications.views import NotificationListView, MarkNotificationsReadView
from core.views import AlertsCountView, HomeView, LandingView, SearchView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("landing/", LandingView.as_view(), name="landing"),
    path("feed/", FeedView.as_view(), name="feed"),
    path("login/", WebLoginView.as_view(), name="auth-login"),
    path("inscription/", RegisterWebView.as_view(), name="auth-register-web"),
    path("logout/", WebLogoutView.as_view(), name="web-logout"),
    path("profil/", MyProfileRedirectView.as_view(), name="profile-me"),
    path("profil/modifier/", ProfileEditView.as_view(), name="profile-edit"),
    path("profil/avatar/supprimer/", AvatarDeleteView.as_view(), name="profile-avatar-delete"),
    path("profil/<int:pk>/", ProfilePublicView.as_view(), name="profile-detail"),
    path("profil/<int:pk>/liste/", FollowersListView.as_view(), name="followers-list"),
    path("profil/<int:pk>/suivre/", FollowToggleView.as_view(), name="user-follow"),
    path("post/nouveau/", PostCreateView.as_view(), name="post-create"),
    path("post/<int:pk>/supprimer/", PostDeleteView.as_view(), name="post-delete"),
    path("post/<int:pk>/like/", LikeToggleView.as_view(), name="post-like"),
    path("post/<int:pk>/comment/", CommentCreateView.as_view(), name="post-comment"),
    path("post/<int:pk>/share/", ShareCreateView.as_view(), name="post-share"),
    path("post/<int:pk>/republish/", RepostCreateView.as_view(), name="post-republish"),
    path("posts/<int:pk>/sauvegarder/", SavePostView.as_view(), name="save-post"),
    path("posts/<int:pk>/retirer-sauvegarde/", UnsavePostView.as_view(), name="unsave-post"),
    path("posts-sauvegardes/", SavedPostsListView.as_view(), name="saved-posts"),
    path("story/nouvelle/", StoryCreateView.as_view(), name="story-create"),
    path("story/<int:pk>/supprimer/", StoryDeleteView.as_view(), name="story-delete"),
    path("comment/<int:pk>/supprimer/", CommentDeleteView.as_view(), name="comment-delete"),
    path("share/<int:pk>/supprimer/", ShareDeleteView.as_view(), name="share-delete"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("notifications/mark-read/", MarkNotificationsReadView.as_view(), name="notifications-mark-read"),
    path("messages/", MessageListView.as_view(), name="messages"),
    path("alerts/count/", AlertsCountView.as_view(), name="alerts-count"),
    path("recherche/", SearchView.as_view(), name="search"),
    path("admin/", admin.site.urls),
]

# Service des fichiers en production
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
