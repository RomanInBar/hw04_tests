from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class CreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='группа-1', slug='slug', description='первая группа'
        )
        cls.group_2 = Group.objects.create(
            title='группа-2', slug='slug_2', description='вторая группа'
        )
        cls.post = Post.objects.create(
            text='текст', author_id=cls.user.id, group_id=cls.group.id
        )

    def setUp(self):
        self.user = CreateFormTest.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post(self):
        """Запись новых постов в базу данных."""
        post_count = Post.objects.count()
        form_fields = {'text': 'Новый пост', 'group': self.group.id}
        response = self.auth_client.post(
            reverse('posts:new_post'), data=form_fields, follow=True
        )
        post = Post.objects.filter(text=form_fields['text']).get()

        var_tests = {
            Post.objects.count(): post_count + 1,
            response.status_code: HTTPStatus.OK,
            form_fields['group']: post.group.id,
            form_fields['text']: post.text,
        }

        for var_one, var_two in var_tests.items():
            with self.subTest(var_one=var_one):
                self.assertEqual(var_one, var_two)

    def test_edit_post(self):
        """Редактирование поста."""
        post_count = Post.objects.count()
        form_fields = {'text': 'Редачим пост', 'group': self.group_2.id}
        resp = self.auth_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id,
                },
            ),
            data=form_fields,
            follow=True,
        )
        edit_post = Post.objects.first()

        var_tests = {
            form_fields['text']: edit_post.text,
            form_fields['group']: edit_post.group.id,
            Post.objects.count(): post_count,
            resp.status_code: HTTPStatus.OK,
        }

        for var_one, var_two in var_tests.items():
            with self.subTest(var_one=var_one):
                self.assertEqual(var_one, var_two)
