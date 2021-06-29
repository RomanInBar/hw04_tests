import shutil
import tempfile
from http import HTTPStatus

from django.test import Client, TestCase
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post, User


class CreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='группа-1',
            slug='slug',
            description='первая группа')
        cls.group_2 = Group.objects.create(
            title='группа-2',
            slug='slug_2',
            description='вторая группа')
        cls.post = Post.objects.create(
            text='текст',
            author_id=1,
            group_id=1)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = CreateFormTest.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post(self):
        """Запись новых постов в базу данных."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='posts/small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_fields = {
            'text': 'Новый пост',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.auth_client.post(
            reverse('posts:new_post'),
            data=form_fields,
            follow=True
        )
        post = Post.objects.filter(text=form_fields['text']).get()

        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=post.id,
                group=post.group.id,
                image=post.image
            ).exists()
        )

    def test_edit_post(self):
        """Редактирование поста."""
        post_count = Post.objects.count()
        form_fields = {
            'text': 'Редачим пост',
            'group': self.group_2.id
        }
        resp = self.auth_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'username': 'user', 'post_id': '1'}),
            data=form_fields,
            follow=True
        )
        edit_post = Post.objects.filter(text=form_fields['text']).get()

        var_tests = {
            form_fields['text']: edit_post.text,
            form_fields['group']: edit_post.group.id,
            Post.objects.count(): post_count,
            resp.status_code: HTTPStatus.OK
        }

        for var_one, var_two in var_tests.items():
            with self.subTest(var_one=var_one):
                self.assertEqual(var_one, var_two)
