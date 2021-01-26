from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates_urls_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }

    def test_about_urls_uses_correct_template(self):
        """Проверка соответствия URL-адресов шаблонам, страниц tech и author.
        """
        for template, url in self.templates_urls_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(
                    response, template,
                    'Проверьте соответствие URL-адресов и шаблонов'
                    ' страниц tech и author.')

    def test_about_urls_exists_user(self):
        """Проверка доступности страниц tech и author."""
        for url in self.templates_urls_names.values():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, 200,
                    'Проверьте доступность страниц tech и author.')
