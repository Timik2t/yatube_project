import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

SLUG_1 = 'Test_slug_1'
SLUG_2 = 'Test_slug_2'
USERNAME = 'TestTestov'
USERNAME_2 = 'IvanIvanov'
CREATE_POST = reverse('posts:post_create')
PROFILE = reverse('posts:profile', kwargs={'username': USERNAME})
LOGIN_REDIRECT = f"{reverse('login')}?next="
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
UPLOADED_NEW = SimpleUploadedFile(
    name='new_small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
UPLOADED_EDIT = SimpleUploadedFile(
    name='edit_small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
UPLOADED_ANOTHER = SimpleUploadedFile(
    name='another_small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
IMAGE_UPLOAD_TO = Post.image.field.upload_to


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
        cls.group_edit = Group.objects.create(
            title='Измененная группа',
            slug=SLUG_2,
            description='Измененное описание',
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
        cls.POST_EDIT_REDIRECT = f'{LOGIN_REDIRECT}{cls.POST_EDIT}'
        cls.POST_DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )
        cls.ADD_COMMENT = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.pk}
        )
        cls.POST_DETAIL_REDIRECT = f'{LOGIN_REDIRECT}{cls.POST_DETAIL}'
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.user_2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        Post.objects.all().delete()
        form_data = {
            'text': 'Новый текст',
            'group': self.group.pk,
            'image': UPLOADED_NEW,
        }
        response = self.author.post(
            CREATE_POST,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertRedirects(response, PROFILE)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(
            post.image.name,
            IMAGE_UPLOAD_TO + form_data['image'].name
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'текст измененный',
            'group': self.group_edit.pk,
            'image': UPLOADED_EDIT,
        }
        response = self.author.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(
            post.image.name,
            IMAGE_UPLOAD_TO + form_data['image'].name
        )
        self.assertRedirects(response, self.POST_DETAIL)

    def test_not_author_edit_post(self):
        """Не автор не может редактировать пост"""
        form_data = {
            'text': 'Текст еще раз другой',
            'group': self.group_edit.pk,
            'image': UPLOADED_ANOTHER,
        }
        CASES = [
            [self.another, self.POST_DETAIL],
            [self.guest, self.POST_EDIT_REDIRECT]
        ]
        for client, redirect in CASES:
            response = client.post(
                self.POST_EDIT,
                data=form_data,
                follow=True
            )
            post = Post.objects.get(pk=self.post.pk)
            self.assertEqual(self.post.text, post.text)
            self.assertEqual(self.post.author, post.author)
            self.assertEqual(self.group.pk, post.group.pk)
            self.assertEqual(self.post.image, post.image)
            self.assertRedirects(response, redirect)

    def test_add_comment(self):
        """Валидная форма добавляет комментарий"""
        Comment.objects.all().delete()
        form_data = {
            'text': 'текст комментария',
        }
        response = self.author.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertRedirects(response, self.POST_DETAIL)

    def test_guest_add_post(self):
        """Неавторизованный пользователь не может создать пост"""
        Post.objects.all().delete()
        form_data = {
            'text': 'Текст измененный',
            'group': self.group.pk,
            'image': UPLOADED,
        }
        self.guest.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_guess_add_comment(self):
        """Неавторизованный пользователь не может оставить коммент."""
        Comment.objects.all().delete()
        form_data = {
            'text': 'текст комментария',
        }
        self.guest.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 0)
