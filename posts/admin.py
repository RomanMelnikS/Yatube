from django.contrib import admin
from django.utils.html import format_html

from .models import Comment, Group, Post, Follow


class CommentInLine(admin.StackedInline):
    model = Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'image_tag', 'image')
    readonly_fields = ('image_tag',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    inlines = [CommentInLine]

    def image_tag(self, post):
        if post.image:
            return format_html(
                '<img src="{0}" style="max-width: 100%"/>',
                post.image.url
            )
    image_tag.short_description = 'Превью'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description', 'slug',)
    search_fields = ('title',)
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
