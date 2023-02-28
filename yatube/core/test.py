from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class ViewTestClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_404_page(self):
        response = self.client.get('page')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
