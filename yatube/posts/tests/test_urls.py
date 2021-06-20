from django.test import Client, TestCase
from django.urls.base import reverse

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.Bob = User.objects.create_user(username='Bob')
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
        self.auth_client = Client()
        self.Bob = Client()
        self.auth_client.force_login(StaticURLTests.user)
        self.Bob.force_login(StaticURLTests.Bob)

    def test_templates_urls(self):
        """Вывод верных шаблонов по заданному адресу."""
        templates_url_names = {
            '/': 'index.html',
            '/group/slug/': 'group.html',
            '/new/': 'posts/new_edit_post.html',
            '/user/1/edit/': 'posts/new_edit_post.html'
        }

        for adress, template in templates_url_names.items():
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
            '/group/slug/': 200,
            '/user/1/': 200,
            '/user/': 200,
            '/new': 301,
        }

        for url, code in url_code.items():
            with self.subTest(url=url):
                response = self.quest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    code,
                    'Ошибка в тесте test_code_urls')

    def test_url_redirect(self):
        """Проверка переадресации незарегистрированных пользователей."""
        resp = self.quest_client.get('/user/1/edit/', follow=True)
        self.assertRedirects(resp, reverse('login') + '?next=/user/1/edit/')

    def test_post_edit(self):
        """Проверка возможности редактирования поста разными пользователями."""
        anonym = self.quest_client.get('/user/1/edit/')
        self.assertEqual(anonym.status_code, 302)

        auth_autor = self.auth_client.get('/user/1/edit/')
        self.assertEqual(auth_autor.status_code, 200)

        auth_no_author = self.Bob.post(
            reverse(
                'posts:post_edit',
                kwargs={'username': 'user', 'post_id': '1'}),
            data={
                'text': 'I am not author. Ha-ha!'
            },
            follow=True)
        self.assertRedirects(
            auth_no_author,
            reverse('posts:post', kwargs={'username': 'user', 'post_id': '1'}))
