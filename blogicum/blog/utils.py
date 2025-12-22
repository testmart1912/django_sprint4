from django.db.models import Count
from django.utils import timezone
from .models import Post, Category


def get_published_posts():
    """
    Возвращает QuerySet опубликованных постов.
    Включает только посты, доступные для публичного просмотра.
    """

    return Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('author', 'category', 'location')


def get_posts_with_comments_count():
    """
    Возвращает QuerySet постов с аннотированным количеством комментариев.
    """

    return get_published_posts().annotate(
        comment_count=Count('comments')
    )


def get_paginated_page(request, queryset, per_page=10):
    """
    Возвращает страницу пагинатора для заданного QuerySet.
    """

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


def get_user_posts(username):
    """
    Возвращает все посты пользователя (включая неопубликованные).
    """

    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Post.objects.none()

    return Post.objects.filter(author=user).select_related(
        'author', 'category', 'location'
    ).annotate(comment_count=Count('comments'))


def get_category_posts(category_slug):
    """
    Возвращает опубликованные посты для указанной категории.
    """

    try:
        category = Category.objects.get(
            slug=category_slug,
            is_published=True
        )
    except Category.DoesNotExist:
        return Post.objects.none()

    return get_posts_with_comments_count().filter(category=category)
