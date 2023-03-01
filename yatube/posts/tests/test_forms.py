import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from yatube.settings import BASE_DIR
from posts.models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='User')
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='slug',
            description='Описание',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_authorized_client_post_create(self):
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(form_data['group'], self.group.pk)
        self.assertEqual(self.author.username, 'author')
        self.assertEqual(form_data['text'], 'Данные из формы')
        self.assertEqual(form_data['image'], uploaded)
        self.assertIs(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))

    def test_authorized_post_edit(self):
        post = Post.objects.create(
            text='Текст поста',
            pub_date='Дата обновления',
            author=self.user,
            group=self.group,
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Редактированный текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        self.assertIs(Post.objects.count(), post_count)
        self.assertIs(post.group, self.group)
        self.assertIs(post.author, self.user)
        self.assertIs(post.text, 'Текст поста')
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.pk}))


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='User')
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_client_comment_create(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Данные из формы',
            'post': self.post.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(form_data['post'], self.post.pk)
        self.assertEqual(self.user.username, 'User')
        self.assertEqual(form_data['text'], 'Данные из формы')
        self.assertIs(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}))
