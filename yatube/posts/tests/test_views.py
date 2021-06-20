from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='текст',
            slug='slug',
            description='Это просто очередной тест')
        for object in range(15):
            cls.post = Post.objects.create(
                text='текст',
                pub_date='20.20.2020',
                author_id=1)

    def setUp(self):
        self.user = ViewsTests.user
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_page_use_correct_templates(self):
        """Соответствие шаблонов к url через вызов view."""
        templates_pages = {
            'index.html': reverse('posts:index'),
            'group.html': reverse(
                'group',
                kwargs={'slug': 'slug'}),
            'posts/new_edit_post.html': reverse(
                'posts:new_post')
        }

        for template, page in templates_pages.items():
            with self.subTest(page=page):
                response = self.auth_client.get(page)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Ошибка в test_page_use_correct_templates')

    def test_index_correct_context(self):
        """Проверка context главной страницы."""
        response = self.auth_client.get(reverse('posts:index'))
        first_object = response.context['page'][0]

        post_text_0 = first_object.text

        self.assertEqual(post_text_0, 'текст')

    def test_new_correct_context(self):
        """Проверка context страницы создания поста."""
        response = self.auth_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_group_pages_context(self):
        """Проверка context страницы группы."""
        response = self.auth_client.get(
            reverse('group', kwargs={'slug': 'slug'}))
        self.assertEqual(response.context['group'].title, 'текст'),
        self.assertEqual(response.context['group'].slug, 'slug')
        self.assertEqual(
            response.context['group'].description,
            'Это просто очередной тест')

    def test_paginator(self):
        """Проверка корректной работы пажинатора."""
        posts_in_page = {
            reverse('posts:index'): 10,
            reverse('posts:index') + '?page=2': 5
        }
        for url, posts in posts_in_page.items():
            with self.subTest(url=url):
                resp = self.auth_client.get(url)
                self.assertEqual(
                    len(resp.context['page']),
                    posts,
                    'Ошибка в тесте test_paginator')

    def test_post_with_group(self):
        """Проверка на запись нового поста с указанием группы."""
        form_data = {
            'text': 'New post',
            'group': 1
        }
        for i in range(2):
            self.auth_client.post(
                reverse('posts:new_post'),
                data=form_data,
                follow=True
            )

        posts_in_page = {
            reverse('posts:index') + '?page=2': 7,
            reverse('group', kwargs={'slug': 'slug'}): 2
        }

        for url, posts in posts_in_page.items():
            with self.subTest(url=url):
                resp = self.auth_client.get(url)
                posts_count = len(resp.context['page'])
                self.assertEqual(
                    posts_count,
                    posts,
                    'Ошибка в тесте test_post_with_group')
