from django.test import TestCase

from ..models import Comment, Group, Post, User
from ..settings import LIMIT_STR_TEXT

SLUG = 'Test_slug_1'
USERNAME = 'TestTestov'


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комент',
            post=cls.post
        )

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        self.assertEqual(
            str(self.post),
            self.post.DISPLAY.format(
                text=self.post.text,
                LIMIT_STR_TEXT=LIMIT_STR_TEXT,
                author=self.post.author.username,
                group=self.post.group
            ),
            'У модели Post некорректно работает __str__'
        )

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(
            str(self.group),
            self.group.title,
            'У модели Group некорректно работает __str__'
        )

    def test_comments_have_correct_object_names(self):
        """Проверяем, что у модели Comments корректно работает __str__."""
        self.assertEqual(
            str(self.comment),
            self.comment.DISPLAY.format(
                text=self.comment.text,
                LIMIT_STR_TEXT=LIMIT_STR_TEXT,
                author=self.comment.author.username,
            ),
            'У модели Comment некорректно работает __str__'
        )
