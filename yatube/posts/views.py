from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    template = 'posts/index.html'
    # Строку, которую надо вывести на страницу, тоже сохраним в переменную
    title = 'Это главная страница проекта Yatube'
    # Словарь с данными принято называть context
    context = {
        # В словарь можно передать переменную
        'title': title,
    }
    # Третьим параметром передаём словарь context
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    title = 'Здесь будет информация о группах проекта Yatube'
    context = {
        # В словарь можно передать переменную
        'title': title,
    }
    # Третьим параметром передаём словарь context
    return render(request, template, context)
