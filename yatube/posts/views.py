from django.shortcuts import render, get_object_or_404

from .models import Post, Group

LIMIT = 10


def index(request):
    posts = Post.objects.all()[:LIMIT]
    context = {
        'title': 'Последние обновления на сайте',
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:LIMIT]
    context = {
        'group': group,
        'posts': posts,
        'title': f'Записи сообщества {group}',
    }
    return render(request, 'posts/group_list.html', context)
