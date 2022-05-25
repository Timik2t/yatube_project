from http.client import FOUND, NOT_FOUND, OK

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post, User

SLUG = 'Test_slug'
USERNAME_1 = 'TestTestov'
USERNAME_2 = 'IvanIvanov'
INDEX = reverse('posts:index')
CREATE_POST = reverse('posts:post_create')
GROUP_LIST = reverse('posts:group_list', kwargs={'slug': SLUG})
PROFILE = reverse('posts:profile', kwargs={'username': USERNAME_1})
UNEXSISTING = '/unexsisting_page/'
LOGIN_REDIRECT = f"{reverse('login')}?next="
CREATE_POST_REDIRECT = f'{LOGIN_REDIRECT}{CREATE_POST}'
FOLLOW_INDEX = reverse('posts:follow_index')
FOLLOW = reverse('posts:profile_follow', kwargs={'username': USERNAME_1})
UNFOLLOW = reverse('posts:profile_unfollow', kwargs={'username': USERNAME_1})
FOLLOW_REDIRECT = f'{LOGIN_REDIRECT}{FOLLOW}'
UNFOLLOW_REDIRECT = f'{LOGIN_REDIRECT}{UNFOLLOW}'
FOLLOW_INDEX_REDIRECT = f'{LOGIN_REDIRECT}{FOLLOW_INDEX}'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_2 = User.objects.create_user(username=USERNAME_1)
        cls.user = User.objects.create_user(username=USERNAME_2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_2,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комент',
            post=cls.post
        )
        cls.POST_EDIT = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.pk}
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )
        cls.POST_EDIT_REDIRECT = f'{LOGIN_REDIRECT}{cls.POST_EDIT}'
        cls.guest = Client()
        cls.another = Client()
        cls.another.force_login(cls.user)
        cls.author = Client()
        cls.author.force_login(cls.user_2)

    def test_urls_access(self):
        """Проверка доступности страниц"""
        CASES = [
            [INDEX, self.guest, OK],
            [GROUP_LIST, self.guest, OK],
            [self.POST_DETAIL, self.guest, OK],
            [PROFILE, self.guest, OK],
            [CREATE_POST, self.guest, FOUND],
            [CREATE_POST, self.another, OK],
            [self.POST_EDIT, self.guest, FOUND],
            [self.POST_EDIT, self.another, FOUND],
            [self.POST_EDIT, self.author, OK],
            [UNEXSISTING, self.guest, NOT_FOUND],
            [FOLLOW, self.guest, FOUND],
            [FOLLOW, self.another, FOUND],
            [FOLLOW, self.author, FOUND],
            [UNFOLLOW, self.guest, FOUND],
            [UNFOLLOW, self.another, FOUND],
            [UNFOLLOW, self.author, NOT_FOUND],
            [FOLLOW_INDEX, self.guest, FOUND],
            [FOLLOW_INDEX, self.another, OK],
        ]
        for url, client, status in CASES:
            with self.subTest(
                url=url,
                client=client
            ):
                self.assertEqual(
                    client.get(url).status_code,
                    status
                )

    def test_url_redirect(self):
        """Проверка корректоного перенаправления"""
        CASES = [
            [CREATE_POST, self.guest, CREATE_POST_REDIRECT],
            [self.POST_EDIT, self.guest, self.POST_EDIT_REDIRECT],
            [self.POST_EDIT, self.another, self.POST_DETAIL],
            [FOLLOW, self.guest, FOLLOW_REDIRECT],
            [UNFOLLOW, self.guest, UNFOLLOW_REDIRECT],
            [FOLLOW_INDEX, self.guest, FOLLOW_INDEX_REDIRECT],
            [FOLLOW, self.another, PROFILE],
            [UNFOLLOW, self.another, PROFILE],
            [FOLLOW, self.author, PROFILE],
        ]
        for url, client, redirect_url in CASES:
            with self.subTest(
                url=url,
                client=client,
                redirect_url=redirect_url
            ):
                self.assertRedirects(
                    client.get(url, follow=True),
                    redirect_url
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            INDEX: 'posts/index.html',
            GROUP_LIST: 'posts/group_list.html',
            PROFILE: 'posts/profile.html',
            self.POST_DETAIL: 'posts/post_detail.html',
            CREATE_POST: 'posts/create_post.html',
            self.POST_EDIT: 'posts/create_post.html',
            FOLLOW_INDEX: 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.author.get(address),
                    template
                )
