from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user")
        cls.group = Group.objects.create(
            title="текст", slug="slug", description="Это просто очередной тест"
        )
        cls.group_2 = Group.objects.create(
            title="какой-то текст",
            slug="slug_2",
            description="Ёще одна группа",
        )
        for object in range(15):
            cls.post = Post.objects.create(
                text="текст", author_id=cls.user.id, group_id=cls.group.id
            )

    def setUp(self):
        self.auth_client = Client()
        self.quest_client = Client()
        self.auth_client.force_login(ViewsTests.user)
        self.posts_count = Post.objects.count()

    def test_page_use_correct_templates(self):
        """Соответствие шаблонов к url через вызов view."""
        templates_pages = {
            "index.html": reverse("posts:index"),
            "group.html": reverse("group", kwargs={"slug": self.group.slug}),
            "posts/new_edit_post.html": reverse("posts:new_post"),
        }

        for template, page in templates_pages.items():
            with self.subTest(page=page):
                response = self.auth_client.get(page)
                self.assertTemplateUsed(
                    response,
                    template,
                    "Ошибка в test_page_use_correct_templates",
                )

    def logic_for_tests(self, value):
        """Логика для тестов главной и страницы профиля."""
        first_object = value.context["page"][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_slug = first_object.group.slug
        post_date_0 = first_object.pub_date
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_date_0, self.post.pub_date)
        self.assertEqual(post_slug, self.group.slug)

    def test_index_page_context(self):
        """Проверка context главной страницы."""
        resp = self.quest_client.get(reverse("posts:index"))
        self.logic_for_tests(resp)

    def test_profile_page_context(self):
        """Проверка context страницы профиля."""
        resp = self.auth_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        self.logic_for_tests(resp)
        self.assertEqual(resp.context["posts"].count(), Post.objects.count())

    def test_post_correct_context(self):
        """Проверка context страницы поста."""
        response = self.auth_client.get(
            reverse(
                "posts:post",
                kwargs={
                    "username": self.user.username,
                    "post_id": self.post.id,
                },
            )
        )
        resp = response.context["post"]
        self.assertEqual(resp.text, self.post.text)
        self.assertEqual(resp.author, self.post.author)
        self.assertEqual(resp.group, self.group)
        self.assertEqual(resp.pub_date, self.post.pub_date)

    def test_new_edit_correct_context(self):
        """Проверка context страницы создания и редактирования поста."""
        response_1 = self.auth_client.get(reverse("posts:new_post"))
        response_2 = self.auth_client.get(
            reverse(
                "posts:post_edit",
                kwargs={
                    "username": self.user.username,
                    "post_id": self.post.id,
                },
            )
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response_1.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)
                form_field = response_2.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_group_pages_context(self):
        """Проверка context страницы группы."""
        response = self.auth_client.get(f"/group/{self.group.slug}/")
        post_group = response.context["group"]
        post_author = response.context["page"][0]
        self.assertEqual(post_group.title, self.post.text),
        self.assertEqual(post_group.slug, self.group.slug)
        self.assertEqual(post_group.description, self.group.description)
        self.assertEqual(post_author.author, self.post.author)

    def test_paginator(self):
        """Проверка корректной работы пажинатора."""
        posts_on_page = {
            reverse("posts:index"): (10, 5),
            reverse("group", kwargs={"slug": self.group.slug}): (10, 5),
            reverse(
                "posts:profile", kwargs={"username": self.user.username}
            ): (10, 5),
        }

        for url, posts in posts_on_page.items():
            first_page, second_page = posts
            with self.subTest(url=url):
                first = self.auth_client.get(url)
                second = self.auth_client.get((url) + "?page=2")
                self.assertEqual(
                    len(first.context.get("page").object_list),
                    first_page,
                    "Ошибка в тесте test_paginator, первая страница",
                )
                self.assertEqual(
                    len(second.context.get("page").object_list),
                    second_page,
                    "Ошибка в тесте test_paginator, вторая страница",
                )

    def test_post_with_group(self):
        """Проверка на запись нового поста с указанием группы."""
        form_data = {"text": "New post", "group": self.group_2.id}
        for i in range(2):
            self.auth_client.post(
                reverse("posts:new_post"), data=form_data, follow=True
            )

        posts_on_page = {
            reverse("group", kwargs={"slug": self.group.slug}): 10,
            reverse("group", kwargs={"slug": self.group_2.slug}): 2,
        }

        for url, posts in posts_on_page.items():
            with self.subTest(url=url):
                resp = self.auth_client.get(url)
                posts_count = len(resp.context.get("page").object_list)
                self.assertEqual(
                    posts_count, posts, "Ошибка в тесте test_post_with_group"
                )
        resp = self.auth_client.get(reverse("posts:index") + "?page=2")
        self.assertEqual(len(resp.context.get("page").object_list), 7)
