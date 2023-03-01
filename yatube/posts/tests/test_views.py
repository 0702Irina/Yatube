from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from django import forms
from yatube.settings import NUM_POST
from posts.models import Post, Group, User, Follow

User = get_user_model()
post_paginator = 13


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='User')
        cls.group = Group.objects.create(
            title='Первая группа',
            slug='slug',
            description='Описание группы',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            pub_date='Дата обновления',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_attributes(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'slug'}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'User'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': 5}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': 5}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_listview_right_context(self):
        urls = (
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user}),
            reverse('posts:group_list', kwargs={'slug': 'slug'}),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn('page_obj', response.context)
                page_obj = response.context.get('page_obj')
                self.assertEqual(len(page_obj), 1)
                self.check_post_attributes(page_obj[0])

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(
            response.context.get('author'),
            self.user
        )

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug'})
        )
        self.assertIn('group', response.context)
        group = response.context.get('group')
        self.assertEqual(group.title, 'Первая группа')
        self.assertEqual(group.slug, 'slug')

    def test_post_detail_page_show_correct_context(self):
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertIn('post', response.context)
        self.check_post_attributes(response.context.get('post'))

    def test_create_post_show_correct_context(self):
        urls = (
            reverse('posts:post_create'),
            reverse(('posts:post_edit'), kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                form = response.context.get('form')
                self.assertIsInstance(form, forms.ModelForm)
            for field, expected_type in form_fields.items():
                with self.subTest(field=field):
                    self.assertIsInstance(
                        form.fields.get(field),
                        expected_type
                    )

    def test_post_another_group(self):
        self.another_group = Group.objects.create(
            title='Вторая группа',
            slug='slug2',
            description='Вторая группа'
        )

        self.post = Post.objects.create(
            text='текст поста второй группы',
            author=self.user,
            group=self.another_group
        )

        response = self.authorized_client.get(
            reverse('posts:group_list', args={self.another_group.slug}))

        self.assertIn('page_obj', response.context)
        page_obj = response.context.get('page_obj')
        self.assertEqual(len(page_obj), 1)
        self.check_post_attributes(page_obj[0])

    def test_guest_client_cant_comment(self):
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data={'text': 'text'},
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_add_new_comment(self):
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data={'text': 'Комментарий'})
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, 'Комментарий')

    def test_cache(self):
        cache.clear()
        self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.create(text="Очищение кэша", author=self.user)
        response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotIn(post.text, response2.content.decode())
        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:index'))
        self.assertIn(post.text, response3.content.decode())


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='User')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Описание группы',
        )

        for post in range(post_paginator):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Записи группы',
                group=cls.group,
            )

    def test_paginator_first_page(self):
        pages = {
            'posts:index': reverse('posts:index'),
            'posts:group_list': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            'posts:profile': reverse(
                'posts:profile', kwargs={'username': self.user.username},
            )
        }
        for template, reverse_name in pages.items():
            response = self.client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), NUM_POST)

    def test_second_page_contains_three_records(self):
        pages = {
            'posts:index': reverse('posts:index') + '?page=2',
            'posts:group_list': reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}) + '?page=2',
            'posts:profile': reverse(
                'posts:profile',
                kwargs={'username': self.user.username}) + '?page=2',
        }
        for page, reverse_name in pages.items():
            response = self.client.get(reverse_name)
            pag = len(response.context['page_obj'])
            self.assertEqual((pag), post_paginator - NUM_POST)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create(username='user')
        cls.user_following = User.objects.create(username='user_1')
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Текст поста',
        )

    def setUp(self):
        self.following_client = Client()
        self.follower_client = Client()
        self.following_client.force_login(self.user_following)
        self.follower_client.force_login(self.user_follower)

    def test_follow(self):
        follower_count = Follow.objects.count()
        self.follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_following.username}
            )
        )
        self.assertEqual(Follow.objects.count(), follower_count + 1)

    def test_unfollow(self):
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        follower_count = Follow.objects.count()
        self.follower_client.get(reverse(
            'posts:profile_unfollow',
            args=(self.user_following.username,)))
        self.assertEqual(Follow.objects.count(), follower_count - 1)

    def test_new_post_see_follower(self):
        posts = Post.objects.create(
            text=self.post.text,
            author=self.user_following,
        )
        follow = Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post, posts)
        follow.delete()
        response_2 = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response_2.context['page_obj']), 0)
