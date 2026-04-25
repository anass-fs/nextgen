from django.contrib import admin

from apps.posts.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "post_type", "author", "created_at")
    list_filter = ("post_type", "created_at")
    search_fields = ("title", "description")
    raw_id_fields = ("author",)
