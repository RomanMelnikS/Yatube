from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User

AUTHOR_USERNAME = 'PostTestUser'
AUTH_USER_USERNAME = 'TestUser'

GROUP_TITLE = 'Тестовая группа'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-group'

POST_TEXT = 'Тестовый текст'
COMMENT_TEXT = 'Тестовый комментарий'

INDEX_URL = reverse('index')
FOLLOW_INDEX_URL = reverse('follow_index')
GROUP_URL = reverse('group', kwargs={'slug': GROUP_SLUG})
NEW_POST_URL = reverse('new_post')
PROFILE_URL = reverse('profile', kwargs={'username': AUTHOR_USERNAME})


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=AUTHOR_USERNAME)
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )

        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text=COMMENT_TEXT,
        )

    def setUp(self):
        self.user = User.objects.create(username=AUTH_USER_USERNAME)
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

        self.comment_id = PostURLTests.comment.id
        self.post_id = PostURLTests.post.id

        self.POST_URL = reverse(
            'post',
            kwargs={'username': AUTHOR_USERNAME,
                    'post_id': self.post_id}
        )
        self.POST_EDIT_URL = reverse(
            'post_edit',
            kwargs={'username': AUTHOR_USERNAME,
                    'post_id': self.post_id}
        )
        self.ADD_COMMENT_URL = reverse(
            'add_comment',
            kwargs={'username': AUTHOR_USERNAME,
                    'post_id': self.post_id}
        )
        self.FOLLOW_URL = reverse(
            'profile_follow',
            kwargs={'username': AUTHOR_USERNAME}
        )
        self.UNFOLLOW_URL = reverse(
            'profile_unfollow',
            kwargs={'username': AUTHOR_USERNAME}
        )
        self.POST_DELETE_URL = reverse(
            'post_delete',
            kwargs={'username': AUTHOR_USERNAME,
                    'post_id': self.post_id}
        )
        self.COMMENT_DELETE_URL = reverse(
            'delete_comment',
            kwargs={'username': AUTHOR_USERNAME,
                    'comment_id': self.comment_id,
                    'post_id': self.post_id}
        )

        self.templates_urls_names = {
            'index.html': INDEX_URL,
            'follow.html': FOLLOW_INDEX_URL,
            'group.html': GROUP_URL,
            'posts/new_post.html': NEW_POST_URL,
            'posts/profile.html': PROFILE_URL,
            'posts/post.html': self.POST_URL
        }

    def test_urls_uses_correct_template(self):
        """Проверка соответствия URL-адресов шаблонам."""
        for template, url in self.templates_urls_names.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(
                    response, template,
                    'Проверьте соответствие URL-адресов и шаблонов.')

    def test_urls_exists_auth_user(self):
        """Проверка доступности страниц для авторизованного пользователя."""
        for url in self.templates_urls_names.values():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertEqual(
                    response.status_code, 200,
                    'Проверьте доступность страниц авторизованному'
                    ' пользователю.')

    def test_urls_exists_not_auth_user(self):
        """Проверка доступности страниц для неавторизованного пользователя."""
        for url in self.templates_urls_names.values():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertEqual(
                    response.status_code, 200,
                    'Проверьте доступность страниц неавторизованному'
                    ' пользователю.')

    def test_redirect_new_post_not_auth_user(self):
        """Проверка доступности new_post.

        new_post недоступна для неавторизованного
        пользователя и перенаправляет его на login.
        """
        response = self.guest_client.get(NEW_POST_URL, follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/new/'), 302, 200,
            'Проверьте перенаправляете ли, вы неавторизованного пользователя'
            ' с new_post на login.')

    def test_url_post_edit_uses_correct_template(self):
        """Проверка соответствия URL-адреса post_edit шаблону."""
        author = PostURLTests.auth_author
        response = author.get(self.POST_EDIT_URL)
        self.assertTemplateUsed(
            response, 'posts/new_post.html',
            'Проверьте соответствие URL-адреса post_edit'
            ' шаблону new_post.')

    def test_redirect_post_edit_not_auth_user(self):
        """Проверка доступности post_edit.

        post_edit недоступна для неавторизованного
        пользователя и перенаправляет его на post.
        """
        response = self.guest_client.get(self.POST_EDIT_URL, follow=True)
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте перенаправляете ли, вы неавторизованного пользователя'
            ' с post_edit на post.')

    def test_redirect_post_edit_auth_user(self):
        """Проверка доступности post_edit.

        post_edit недоступна для авторизованного
        пользователя(не автора поста) и перенаправляет его на post.
        """
        response = self.auth_client.get(self.POST_EDIT_URL, follow=True)
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте перенаправляете ли, вы авторизованного пользователя'
            ' с post_edit на post.')

    def test_redirect_post_edit_post_author(self):
        """Проверка доступности post_edit.

        post_edit доступна для авторизованного
        пользователя(автора поста).
        """
        author = PostURLTests.auth_author
        response = author.get(self.POST_EDIT_URL)
        self.assertEqual(
            response.status_code, 200,
            'Проверьте доступность страницы post_edit'
            ' автору поста.')

    def test_redirect_post_delete_not_auth_user(self):
        """Проверка доступности post_delete.

        post_delete недоступна для неавторизованного
        пользователя и перенаправляет его на post.
        """
        response = self.guest_client.get(self.POST_DELETE_URL)
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте доступность страницы post_delete'
            ' неавторизованному пользователю.')

    def test_redirect_post_delete_auth_user(self):
        """Проверка доступности post_delete.

        post_delete недоступна для авторизованного
        пользователя(не автора поста) и перенаправляет его на post.
        """
        response = self.auth_client.get(self.POST_DELETE_URL)
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте доступность страницы post_delete'
            ' авторизованному пользователю.')

    def test_redirect_post_delete_post_author(self):
        """Проверка доступности post_delete.

        post_delete доступна для авторизованного
        пользователя(автора поста) и перенаправляет его на post.
        """
        author = PostURLTests.auth_author
        response = author.get(self.POST_DELETE_URL)
        self.assertRedirects(
            response, PROFILE_URL, 302, 200,
            'Проверьте доступность страницы post_delete'
            ' автору поста.')

    def test_redirect_add_comment_auth_user(self):
        """Проверка доступности add_comment.

        add_comment доступна для авторизованного
        пользователя и перенаправляет его на post.
        """
        response = self.auth_client.get(self.ADD_COMMENT_URL, follow=True)
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте перенаправляете ли, вы авторизованного пользователя'
            ' с add_comment на post.')

    def test_redirect_add_comment_not_auth_user(self):
        """Проверка доступности add_comment.

        add_comment недоступна для неавторизованного
        пользователя и перенаправляет его на login.
        """
        response = self.guest_client.get(self.ADD_COMMENT_URL, follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/PostTestUser/1/comment/'), 302, 200,
            'Проверьте перенаправляете ли, вы неавторизованного пользователя'
            ' с add_comment на login.')

    def test_redirect_delete_comment_author(self):
        """Проверка доступности delete_comment.

        delete_comment доступна для авторизованного
        пользователя(автора комментария) и перенаправляет его на post.
        """
        author = PostURLTests.auth_author
        response = author.get(self.COMMENT_DELETE_URL, follow=True)
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте перенаправляете ли, вы автора комментария'
            ' с delete_comment на post.')

    def test_redirect_delete_comment_auth_user(self):
        """Проверка доступности delete_comment.

        delete_comment недоступна для авторизованного
        пользователя(не автора комментария) и перенаправляет его на post.
        """
        response = self.auth_client.get(self.COMMENT_DELETE_URL, follow=True)
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте перенаправляете ли, вы авторизованного пользователя'
            ' с delete_comment на post.')

    def test_redirect_delete_comment_not_auth_user(self):
        """Проверка доступности delete_comment.

        delete_comment недоступна для неавторизованного
        пользователя и перенаправляет его на login.
        """
        response = self.guest_client.get(self.COMMENT_DELETE_URL, follow=True)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/PostTestUser/1/1/delete_comment/'), 302, 200,
            'Проверьте перенаправляете ли, вы не авторизованного пользователя'
            ' с delete_comment на post.')

    def test_redirect_follow_index_not_auth_user(self):
        """Проверка доступности follow_index.

        follow_index не доступен неавторизованному пользователю
        и перенаправит его на login.
        """
        response = self.guest_client.get(FOLLOW_INDEX_URL, follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/follow/'), 302, 200,
            'Проверьте перенаправляете ли, вы неавторизованного пользователя'
            ' с follow_index на login.')

    def test_redirect_profile_follow_not_auth_user(self):
        """Проверка доступности profile_follow.

        profile_follow не доступен неавторизованному пользователю
        и перенаправит его на login.
        """
        response = self.guest_client.get(self.FOLLOW_URL, follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/PostTestUser/follow/'), 302, 200,
            'Проверьте перенаправляете ли, вы неавторизованного пользователя'
            ' с profile_follow на login.')

    def test_redirect_profile_unfollow_not_auth_user(self):
        """Проверка доступности profile_unfollow.

        profile_unfollow не доступен неавторизованному пользователю
        и перенаправит его на login.
        """
        response = self.guest_client.get(self.UNFOLLOW_URL, follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/PostTestUser/unfollow/'), 302, 200,
            'Проверьте перенаправляете ли, вы неавторизованного пользователя'
            ' с profile_unfollow на login.')

    def test_redirect_profile_follow_auth_user(self):
        """Проверка доступности profile_follow.

        profile_follow доступен авторизованному пользователю
        и перенаправит его на profile.
        """
        response = self.auth_client.get(self.FOLLOW_URL, follow=True)
        self.assertRedirects(
            response, PROFILE_URL, 302, 200,
            'Проверьте перенаправляете ли, авторизованного пользователя'
            ' с profile_follow на profile.')

    def test_redirect_profile_unfollow_auth_user(self):
        """Проверка доступности profile_unfollow.

        profile_unfollow доступен авторизованному пользователю
        и перенаправит его на profile.
        """
        response = self.auth_client.get(self.UNFOLLOW_URL, follow=True)
        self.assertRedirects(
            response, PROFILE_URL, 302, 200,
            'Проверьте перенаправляете ли, авторизованного пользователя'
            ' с profile_unfollow на profile.')

    def test_page_not_found(self):
        """Проверка ошибки 404, если страница не найдена."""
        response = self.guest_client.get('/page_not_found/')
        self.assertEqual(
            response.status_code, 404,
            'Проверьте возвращаемую сервером ошибку,'
            ' если страница не найдена.')
        self.assertTemplateUsed(
            response, 'misc/404.html',
            'Проверьте возвращаемый сервером шаблон,'
            ' если страница не найдена.')
