from django.test import Client, TestCase

from posts.models import Post, User


class AboutTestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Bob')
        cls.post = Post.objects.create(
            text='Какой-то текст',
            author_id=1
        )

    def setUp(self):
        self.quest_client = Client()

    def test_about_app(self):
        """
        Тестирование приложения about,
        проверка доступа неавторизованному пользователю
        и отображения страниц.
        """
        request_urls = {
            '/about/author/': (200, 'about/author.html'),
            '/about/tech/': (200, 'about/tech.html')
        }

        for url, value in request_urls.items():
            status, template = value
            with self.subTest(url=url):
                resp = self.quest_client.get(url)
                self.assertEqual(resp.status_code, status)
                self.assertTemplateUsed(resp, template)
