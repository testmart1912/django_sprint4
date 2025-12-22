from django.contrib import admin
from .models import Category, Location, Post, Comment
from django.urls import reverse
from django.utils.html import format_html

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.TabularInline):
    """
    Определение класса, который используется
    для создания встроенных форм для связанных объектов Post.
    """

    model = Post
    extra = 0


class CommentInline(admin.TabularInline):
    """
    Определение класса, который используется
    для создания встроенных форм для связанных объектов Comment.
    """

    model = Comment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('author', 'text', 'created_at')


class CategoryAdmin(admin.ModelAdmin):
    """Класс администрирования для модели Category."""

    inlines = (PostInline,)
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title', 'description')
    list_filter = ('is_published', 'created_at')


class LocationAdmin(admin.ModelAdmin):
    """Класс администрирования для модели Location."""

    inlines = (PostInline,)
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created_at')


class PostAdmin(admin.ModelAdmin):
    """Класс администрирования для модели Post."""

    list_display = (
        'title',
        'author',
        'category',
        'is_published',
        'pub_date',
        'created_at',
        'comment_count',
        'is_available'
    )
    list_editable = ('is_published',)
    list_filter = ('is_published', 'category', 'author', 'pub_date', 'created_at')
    search_fields = ('title', 'text', 'author__username')
    list_display_links = ('title',)
    inlines = (CommentInline,)

    def comment_count(self, obj):
        return obj.get_comment_count()
    comment_count.short_description = 'Комментарии'

    def is_available(self, obj):
        return obj.is_available()
    is_available.boolean = True
    is_available.short_description = 'Доступен'


class CommentAdmin(admin.ModelAdmin):
    """Класс администрирования для модели Comment."""

    list_display = ('short_text', 'author', 'post_link', 'created_at')
    list_filter = ('created_at', 'author', 'post')
    search_fields = ('text', 'author__username', 'post__title')
    list_display_links = ('short_text',)
    readonly_fields = ('created_at',)

    def short_text(self, obj):
        if len(obj.text) > 50:
            return obj.text[:47] + '...'
        return obj.text
    short_text.short_description = 'Текст комментария'

    def post_link(self, obj):
        url = reverse('admin:blog_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title[:30])
    post_link.short_description = 'Пост'


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Comment, CommentAdmin)
