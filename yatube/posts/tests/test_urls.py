from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from posts.models import Post, Group, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='User')
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
            id=5,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_url_exists_at_desired_location(self):
        urls_post = (
            '/',
            '/group/slug/',
            '/profile/User',
            '/posts/5/',
        )
        for url in urls_post:
            response = self.client.get(url)
            self.assertTrue(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_anonymous_login(self):
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_url_exists_at_author_location(self):
        response = self.authorized_author.get('/posts/5/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/slug/': 'posts/group_list.html',
            '/profile/User/': 'posts/profile.html',
            '/posts/5/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/5/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
