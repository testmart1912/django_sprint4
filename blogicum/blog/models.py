from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дата и время в будущем — '
        'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        upload_to='blogs_images', 
        null=True, 
        blank=True,
        verbose_name='Фото'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

    def is_available(self):
        """
        Проверяет, доступен ли пост для публичного просмотра.
        """
        return (
            self.is_published 
            and self.category.is_published 
            and self.pub_date <= timezone.now()
        )

    def get_comment_count(self):
        """
        Возвращает количество комментариев к посту.
        """
        return self.comments.count()


class Comment(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Автор комментария',
    )
    post = models.ForeignKey(
        Post, 
        related_name='comments', 
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Пост'
    )
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий от {self.author} к "{self.post.title[:30]}..."'

    def short_text(self):
        """Короткая версия текста для отображения."""
        if len(self.text) > 50:
            return self.text[:47] + '...'
        return self.text
    short_text.short_description = 'Текст'
