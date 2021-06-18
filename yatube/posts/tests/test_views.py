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
        response = self.auth_client.get(reverse('posts:index'))
        first_object = response.context['page'][0]

        post_text_0 = first_object.text

        self.assertEqual(post_text_0, 'текст')

    def test_new_correct_context(self):
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
        response = self.auth_client.get(
            reverse('group', kwargs={'slug': 'slug'}))
        self.assertEqual(response.context['group'].title, 'текст'),
        self.assertEqual(response.context['group'].slug, 'slug')
        self.assertEqual(
            response.context['group'].description,
            'Это просто очередной тест')

    def test_paginator_first(self):
        response = self.auth_client.get(reverse('posts:index'))
        print(response.context.get('page').__dict__)
        self.assertEqual(response.context.get('page').object_list.count(), 10)

    def test_paginator_second(self):
        response = self.auth_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('page').objects.count(), 5)


# *************************************************************************************************
