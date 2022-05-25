from django.test import TestCase
from django.urls import reverse

from ..urls import app_name

SLUG = 'Test_slug_1'
USERNAME = 'TestTestov'
POST_ID = 1
CASES = [
    ['/', 'index', []],
    [f'/group/{SLUG}/', 'group_list', [SLUG]],
    [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
    [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
    [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
    ['/create/', 'post_create', []],
    [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
    [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
    [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
    ['/follow/', 'follow_index', []],
]


class PostModelTests(TestCase):
    def test_correct_reversed_url(self):
        for url, name, args in CASES:
            """Проверка корректности маршрутов  url"""
            self.assertEqual(
                url,
                reverse(f'{app_name}:{name}', args=args),
            )
