import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


from ..models import Follow, Group, Post, User
from ..settings import PAGINATOR_LIMIT

SLUG_1 = 'Test_slug_1'
SLUG_2 = 'Test_slug_2'
USERNAME = 'TestTestov'
USERNAME_2 = 'IvanIvanov'
INDEX = reverse('posts:index')
INDEX_PAGE_2 = INDEX + '?page=2'
CREATE_POST = reverse('posts:post_create')
GROUP_LIST_1 = reverse('posts:group_list', kwargs={'slug': SLUG_1})
GROUP_LIST_1_PAGE_2 = GROUP_LIST_1 + '?page=2'
GROUP_LIST_2 = reverse('posts:group_list', kwargs={'slug': SLUG_2})
PROFILE = reverse('posts:profile', kwargs={'username': USERNAME})
PROFILE_PAGE_2 = PROFILE + '?page=2'
SECOND_PAGE_POSTS_COUNT = 3
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
FOLLOW_INDEX = reverse('posts:follow_index')
FOLLOW_INDEX_PAGE_2 = FOLLOW_INDEX + '?page=2'
FOLLOW = reverse('posts:profile_follow', kwargs={'username': USERNAME})
UNFOLLOW = reverse('posts:profile_unfollow', kwargs={'username': USERNAME})


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG_1,
            description='Тестовое описание',
        )
        cls.second_group = Group.objects.create(
            title='Тестовая группа 2',
            slug=SLUG_2,
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=UPLOADED
        )
        cls.POST_EDIT = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.pk}
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_2 = Client()
        cls.authorized_2.force_login(cls.user_2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        cache.clear()
        Follow.objects.create(
            user=self.user_2,
            author=self.user
        )
        post_obj_urls = {
            INDEX: 'page_obj',
            GROUP_LIST_1: 'page_obj',
            PROFILE: 'page_obj',
            self.POST_DETAIL: 'post',
            FOLLOW_INDEX: 'page_obj',
        }
        for url, post_obj in post_obj_urls.items():
            post = self.authorized_2.get(url).context[post_obj]
            if post_obj == 'page_obj':
                self.assertEqual(len(post), 1)
                post = post[0]
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group, self.post.group)
            self.assertEqual(post.pk, self.post.pk)
            self.assertEqual(post.image, self.post.image)

    def test_post_in_another(self):
        """Пост не попал в чужие ленты"""
        URLS = [GROUP_LIST_2, FOLLOW_INDEX]
        for url in URLS:
            with self.subTest(url=url):
                self.assertNotIn(
                    self.post,
                    self.authorized_2.get(url).context['page_obj']
                )

    def test_group_in_group_list(self):
        """Проверка группы в контексте групп-ленты"""
        group = self.authorized_client.get(GROUP_LIST_1).context.get('group')
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.pk, self.group.pk)

    def test_author_in_profile(self):
        """Проверка автора в контесте профиля"""
        self.assertEqual(
            self.authorized_client.get(PROFILE).context.get('author'),
            self.user
        )

    def test_follow_user(self):
        """Проверка подписки."""
        self.authorized_2.get(FOLLOW)
        self.assertTrue(Follow.objects.filter(
            user=self.user_2,
            author=self.user).exists()
        )

    def test_unfollow_user(self):
        """Проверка отписки."""
        Follow.objects.create(
            user=self.user_2,
            author=self.user
        )
        self.authorized_2.get(UNFOLLOW)
        self.assertFalse(Follow.objects.filter(
            user=self.user_2,
            author=self.user).exists()
        )

    def test_caches_index(self):
        """Проверка кеширования страницы Index."""
        self.assertNotEqual(Post.objects.count(), 0)
        response_before = self.authorized_client.get(INDEX)
        Post.objects.all().delete()
        response_after = self.authorized_client.get(INDEX)
        self.assertEqual(response_before.content, response_after.content)
        cache.clear()
        self.assertNotEqual(
            response_before.content,
            self.authorized_client.get(INDEX).content
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.another = Client()
        cls.another.force_login(cls.user_2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG_1,
            description='Тестовое описание',
        )
        cls.posts = Post.objects.bulk_create(
            Post(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            ) for i in range(PAGINATOR_LIMIT + SECOND_PAGE_POSTS_COUNT)
        )
        Follow.objects.create(
            user=cls.user_2,
            author=cls.user
        )

    def test_paginator(self):
        """Paginator работает корректно"""
        cache.clear()
        urls_posts_count = [
            [INDEX, PAGINATOR_LIMIT],
            [GROUP_LIST_1, PAGINATOR_LIMIT],
            [PROFILE, PAGINATOR_LIMIT],
            [INDEX_PAGE_2, SECOND_PAGE_POSTS_COUNT],
            [GROUP_LIST_1_PAGE_2, SECOND_PAGE_POSTS_COUNT],
            [PROFILE_PAGE_2, SECOND_PAGE_POSTS_COUNT],
            [FOLLOW_INDEX, PAGINATOR_LIMIT],
            [FOLLOW_INDEX_PAGE_2, SECOND_PAGE_POSTS_COUNT],
        ]
        for url, count in urls_posts_count:
            response = self.another.get(url)
            self.assertEqual(
                len(response.context['page_obj']),
                count
            )
