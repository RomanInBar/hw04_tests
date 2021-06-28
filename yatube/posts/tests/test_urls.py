from http import HTTPStatus

from django.test import Client, TestCase
from django.urls.base import reverse

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.Bob = User.objects.create_user(username='Bob')
        cls.group = Group.objects.create(
            title='Тестовый тест титла',
            slug='slug',
            description='Это просто очередной тест'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст для теста',
            author_id=1
        )

    def setUp(self):
        self.quest = Client()
        self.auth_client = Client()
        self.Bob = Client()
        self.auth_client.force_login(StaticURLTests.user)
        self.Bob.force_login(StaticURLTests.Bob)

    def test_templates_urls(self):
        """Вывод верных шаблонов по заданному адресу."""
        templates_url_names = {
            '/': ('index.html', self.quest),
            f'/group/{self.group.slug}/': ('group.html', self.quest),
            '/new/': ('posts/new_edit_post.html', self.auth_client),
            f'/{self.user.username}/{self.post.id}/edit/': (
                'posts/new_edit_post.html',
                self.auth_client)
        }

        for adress, values in templates_url_names.items():
            template, client = values
            with self.subTest(adress=adress):
                response = client.get(adress)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Ошибка в test_templates_urls')

    def test_code_urls(self):
        """Ответ сервера на запрос клиента."""
        url_code = {
            '/': (HTTPStatus.OK, self.quest),
            f'/group/{self.group.slug}/': (HTTPStatus.OK, self.quest),
            f'/{self.user.username}/{self.post.id}/': (
                HTTPStatus.OK, self.quest),
            f'/{self.user.username}/': (HTTPStatus.OK, self.quest),
            '/new/': (HTTPStatus.OK, self.auth_client)
        }

        for url, values in url_code.items():
            code, client = values
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(
                    response.status_code,
                    code,
                    'Ошибка в тесте test_code_urls')

    def test_url_redirect(self):
        """Проверка переадресации незарегистрированных пользователей."""
        resp = self.quest.get(
            f'/{self.user.username}/{self.post.id}/edit/',
            follow=True)
        self.assertRedirects(
            resp,
            reverse('login') + f'?next=/{self.user.username}'
            f'/{self.post.id}/edit/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Проверка возможности редактирования поста разными пользователями."""
        anonym = self.quest.get(f'/{self.user.username}/{self.post.id}/edit/')
        self.assertRedirects(
            anonym,
            reverse('login') + f'?next=/{self.user.username}'
            f'/{self.post.id}/edit/')

        auth_autor = self.auth_client.get(
            f'/{self.user.username}/{self.post.id}/edit/')
        self.assertEqual(auth_autor.status_code, HTTPStatus.OK)

        auth_no_author = self.Bob.post(
            f'/{self.user.username}/{self.post.id}/edit/',
            data={
                'text': 'I am not author. Ha-ha!'
            },
            follow=True)

        self.assertRedirects(
            auth_no_author,
            reverse(
                'posts:post',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id}))
