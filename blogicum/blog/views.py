from .forms import CommentForm, PostForm, UserProfileForm
from .models import Post, Category, Comment
from .utils import (
    get_posts_with_comments_count,
    get_paginated_page,
    get_user_posts,
    get_category_posts,
)
from django.views.generic import ListView, CreateView
from django.views.generic import UpdateView, DeleteView, DetailView
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy, reverse


class PostListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        return get_posts_with_comments_count().order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = get_paginated_page(
            self.request, 
            self.get_queryset(),
            per_page=self.paginate_by
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    login_url = '/login/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.object.author.username
        return reverse('blog:profile', args=[username])


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        self.object = self.get_object()
        return (
            self.request.user.is_authenticated
            and self.object.author == self.request.user
        )

    def dispatch(self, request, *args, **kwargs):
        if not self.test_func():
            return redirect(reverse(
                'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
            ))
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.object.pk}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author=self.request.user)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        if post.author == self.request.user:
            return post

        if post.is_available():
            return post

        raise Http404('Страница не найдена')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        comments = post.comments.all().order_by('created_at')
        context['form'] = CommentForm()
        context['comments'] = comments
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs['username']
        return get_user_posts(username).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'profile' not in context:
            context['profile'] = get_object_or_404(
                User, username=self.kwargs['username']
            )
        context['page_obj'] = get_paginated_page(
            self.request,
            self.get_queryset(),
            per_page=self.paginate_by
        )
        return context


class CategoryPostsView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/category.html'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return get_category_posts(category_slug).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, 
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        context['page_obj'] = get_paginated_page(
            self.request,
            self.get_queryset(),
            per_page=self.paginate_by
        )
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.object.username}
        )

    def get_object(self):
        return self.request.user


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comments.html'

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse('blog:post_detail', kwargs={'post_id': post_id})

    def form_valid(self, form):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise PermissionDenied(
                'Вы не авторизованы для редактирования этого комментария.'
            )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, id=comment_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.kwargs.get('post_id')
        return context


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise PermissionDenied(
                'Вы не авторизованы для удаления этого комментария.'
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse_lazy('blog:post_detail', kwargs={'post_id': post_id})

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
