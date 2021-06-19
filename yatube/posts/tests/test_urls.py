from django.test import Client, TestCase

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        Group.objects.create(
            title='Тестовый тест титла',
            slug='slug',
            description='Это просто очередной тест'
        )
        Post.objects.create(
            text='Тестовый текст для теста',
            pub_date='20.20.2020',
            author_id=1
        )

    def setUp(self):
        self.quest_client = Client()
        self.user = StaticURLTests.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_templates_urls(self):
        """Вывод верных шаблонов по заданному адресу."""
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/slug/',
            'posts/new_edit_post.html': '/new/'
        }

        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.auth_client.get(adress)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Ошибка в test_templates_urls')

    def test_code_urls(self):
        """Ответ сервера на запрос клиента."""
        url_code = {
            '/': 200,
            '/group/slug/': 200
        }

        url_code_auth = {
            '/new': 301
        }

        for url, code in url_code.items():
            with self.subTest(url=url):
                response = self.quest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    code,
                    'Ошибка в test_code_urls, пользователь не зарегистирован')

        for url, code in url_code_auth.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertEqual(
                    response.status_code,
                    code,
                    'Ошибка в test_code_urls, пользователь зарегистрирован')
