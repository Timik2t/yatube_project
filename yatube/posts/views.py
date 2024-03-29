from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .settings import CACHE_IN_S, PAGINATOR_LIMIT


def get_page(request, list):
    return Paginator(list, PAGINATOR_LIMIT).get_page(
        request.GET.get('page')
    )


@cache_page(CACHE_IN_S, key_prefix='index_page')
def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': get_page(
            request,
            Post.objects.all()
        ),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_page(request, group.posts.all()),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': get_page(request, author.posts.all()),
        'following':
            (request.user != author)
            and request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user, author=author).exists()
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': CommentForm()
    })


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', {
        'post': post,
        'form': form,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj':
            get_page(request, Post.objects.filter(
                author__following__user=request.user)),
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=author.username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow.objects,
        user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:profile', username=username)


@login_required
def add_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_like = False
    for like in post.likes.all():
        if like == request.user:
            is_like = True
            break
    if not is_like:
        post.likes.add(request.user)
    if is_like:
        post.likes.remove(request.user)
    return redirect(request.POST.get('text'))
