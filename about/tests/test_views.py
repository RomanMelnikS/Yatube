from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }

    def test_about_pages_uses_correct_template(self):
        """Проверка соответствия шаблонов URL-адресам, страниц tech и author.
        """
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(
                    response, template,
                    'Проверьте соответствие URL-адресов и шаблонов'
                    ' страниц tech и author.')

    def test_about_page_exists_user(self):
        """Проверка доступности страниц tech и author."""
        for reverse_name in self.templates_pages_names.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    response.status_code, 200,
                    'Проверьте доступность страниц tech и author.')
