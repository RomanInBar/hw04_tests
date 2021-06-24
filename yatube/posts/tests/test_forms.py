from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User


class CreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.post = Post.objects.create(
            text='текст',
            pub_date='20.20.2020',
            author_id=1)

    def setUp(self):
        self.user = CreateFormTest.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post(self):
        """Запись новых постов в базу данных."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост'
        }
        response = self.auth_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )

        self.assertNotEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        """Редактирование поста."""
        text = Post.objects.get(id=1)
        resp = self.auth_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'username': 'user', 'post_id': '1'}),
            data={
                'text': 'Редачим пост'
            },
            follow=True
        )
        new_text = Post.objects.get(id=1)
        self.assertNotEqual(text.text, new_text.text)
        self.assertEqual(resp.status_code, 200)
