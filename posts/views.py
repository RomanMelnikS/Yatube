from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def pagination(objects_list, items, request):
    paginator = Paginator(objects_list, items)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page, paginator


def index(request):
    post_list = Post.objects.select_related('group')
    page, paginator = pagination(post_list, 10, request)
    return render(
        request, 'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page, paginator = pagination(post_list, 10, request)
    return render(
        request, 'group.html',
        {'page': page, 'paginator': paginator,
         'group': group}
    )


@login_required
def new_post(request):
    form = PostForm(
        request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(
        request, 'posts/new_post.html',
        {'form': form}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page, paginator = pagination(post_list, 5, request)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists()
        return render(
            request, 'posts/profile.html',
            {'page': page, 'paginator': paginator,
             'author': author, 'following': following}
        )
    return render(
            request, 'posts/profile.html',
            {'page': page, 'paginator': paginator,
             'author': author}
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    comments = post.comments.all()
    page, paginator = pagination(comments, 5, request)
    form = CommentForm(request.POST or None)
    return render(
        request, 'posts/post.html',
        {'author': author, 'post': post,
         'form': form, 'comments': comments,
         'page': page, 'paginator': paginator}
    )


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if request.user != author:
        return redirect('post', author, post_id)
    if form.is_valid():
        form.save()
        return redirect('post', author, post_id)
    return render(
        request, 'posts/new_post.html',
        {'form': form, 'post': post,
         'is_edit': True}
    )


def post_delete(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    if request.user != author:
        return redirect('post', author, post_id)
    post.delete()
    return redirect('profile', author)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('post', author, post_id)


@login_required
def delete_comment(request, username, post_id, comment_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.author:
        comment.delete()
        return redirect('post', author, post_id)
    return redirect('post', author, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page, paginator = pagination(post_list, 10, request)
    return render(
        request, 'follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', author)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(
        request,
        'misc/500.html',
        status=500
    )
