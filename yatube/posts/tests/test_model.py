from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста, для проверки метода __str__',
        )

    def test_models_have_correct_str_post(self):
        self.assertEqual(str(self.post), self.post.text[:15])

    def test_verbose_name_post(self):
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'По дате изменения',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text_post(self):
        field_help_texts = {
            'text': 'Введите в окне текст нового поста',
            'author': 'Выбирете автора из списка',
            'group': 'Выбирете группу из списка',
            'image': 'Выберете картинку',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.group = Group.objects.create(
            title='Название групп',
            slug='Слаг группы',
            description='Описание группы',
        )

    def test_models_have_correct_str_group(self):
        self.assertEqual(self.group.title, str(self.group))

    def test_verbose_name_grop(self):
        field_verboses = {
            'title': 'Группы',
            'slug': 'слаг для URL',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text_group(self):
        field_help_texts = {
            'title': 'Название группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).
                    help_text, expected_value
                )
