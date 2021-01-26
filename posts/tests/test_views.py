import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

AUTHOR_USERNAME = 'PostTestUser'
FOLLOWER_USERNAME = 'FollowTestUser'
AUTH_USER_USERNAME = 'TestUser'

GROUP_TITLE = 'Тестовая группа'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-group'

ANOTHER_GROUP_TITLE = 'Другая тестовая группа'
ANOTHER_GROUP_SLUG = 'another-test-group'
ANOTHER_GROUP_DESCRIPTION = 'Другое тестовое описание'

POST_TEXT = 'Тестовый текст'
POST_IMAGE = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

POST_FOR_COMMENT_TEXT = 'Тестовый текст для комментариев'
COMMENT_TEXT = 'Тестовый комментарий'

INDEX_URL = reverse('index')
FOLLOW_INDEX_URL = reverse('follow_index')
GROUP_URL = reverse('group', kwargs={'slug': GROUP_SLUG})
ANOTHER_GROUP_URL = reverse('group', kwargs={'slug': ANOTHER_GROUP_SLUG})
NEW_POST_URL = reverse('new_post')
PROFILE_URL = reverse('profile', kwargs={'username': AUTHOR_USERNAME})

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create(username=AUTHOR_USERNAME)
        cls.user = User.objects.create(username=FOLLOWER_USERNAME)

        Follow.objects.create(user=cls.user, author=cls.author)

        cls.following_user = Client()
        cls.following_user.force_login(cls.user)

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=POST_IMAGE,
            content_type='image/gif'
        )

        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )

        cls.another_group = Group.objects.create(
            title=ANOTHER_GROUP_TITLE,
            slug=ANOTHER_GROUP_SLUG,
            description=ANOTHER_GROUP_DESCRIPTION
        )

        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=COMMENT_TEXT,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create(username=AUTH_USER_USERNAME)
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

        self.post_id = PostViewsTests.post.id
        self.comment_id = PostViewsTests.comment.id

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

        self.templates_pages_names = {
            'index.html': INDEX_URL,
            'follow.html': FOLLOW_INDEX_URL,
            'group.html': GROUP_URL,
            'posts/new_post.html': NEW_POST_URL,
            'posts/profile.html': PROFILE_URL,
            'posts/post.html': self.POST_URL,
        }

    def test_pages_uses_correct_template(self):
        """Проверка соответствия шаблонов URL-адресам."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(template=template):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(
                    response, template,
                    'Проверьте соответствие URL-адресов и шаблонов.')

    def test_page_post_edit_uses_correct_template(self):
        """Проверка соответствия URL-адреса post_edit шаблону."""
        author = PostViewsTests.auth_author
        response = author.get(self.POST_EDIT_URL)
        self.assertTemplateUsed(
            response, 'posts/new_post.html',
            'Проверьте соответствие URL-адреса post_edit'
            ' шаблону new_post.')

    def test_index_page_show_correct_context(self):
        """Проверка context шаблона index."""
        response = self.auth_client.get(INDEX_URL)
        self.assertEqual(
            response.context.get('page')[0].text,
            POST_TEXT,
            'Проверьте текст в context главной страницы.')
        self.assertEqual(
            response.context.get('page')[0].author.username,
            AUTHOR_USERNAME,
            'Проверьте автора в context главной страницы.')
        self.assertEqual(
            response.context.get('page')[0].group.title,
            GROUP_TITLE,
            'Проверьте группу в context главной страницы.')
        self.assertEqual(
            response.context.get('page')[0].image,
            'posts/small.gif',
            'Проверьте картинку в context главной страницы.')

    def test_group_page_show_correct_context(self):
        """Проверка context шаблона group."""
        response = self.auth_client.get(GROUP_URL)
        self.assertEqual(
            response.context.get('group').title,
            GROUP_TITLE,
            'Проверьте заголовок в context страницы группы.')
        self.assertEqual(
            response.context.get('group').description,
            GROUP_DESCRIPTION,
            'Проверьте описание в context страницы группы.')
        self.assertEqual(
            response.context.get('group').slug,
            GROUP_SLUG,
            'Проверьте слаг в context страницы группы.')
        self.assertEqual(
            response.context.get('page')[0].text,
            POST_TEXT,
            'Проверьте текст в context страницы группы.')
        self.assertEqual(
            response.context.get('page')[0].author.username,
            AUTHOR_USERNAME,
            'Проверьте автора в context страницы группы.')
        self.assertEqual(
            response.context.get('page')[0].image,
            'posts/small.gif',
            'Проверьте картинку в context страницы группы.')

    def test_new_post_page_show_correct_context(self):
        """Проверка context шаблона new_post."""
        response = self.auth_client.get(NEW_POST_URL)
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field, expected,
                    'Проверьте context страницы добавления записи.')

    def test_post_edit_page_show_correct_context(self):
        """Проверка context шаблона post_edit."""
        author = PostViewsTests.auth_author
        response = author.get(self.POST_EDIT_URL)
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field, expected,
                    'Проверьте context страницы редактирования записи.')

    def test_post_page_show_correct_context(self):
        """Проверка context шаблона post."""
        response = self.auth_client.get(self.POST_URL)
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(
            form_field, forms.CharField,
            'Проверьте форму комментария в context страницы отдельного поста.')
        self.assertEqual(
            response.context.get('author').username,
            AUTHOR_USERNAME,
            'Проверьте автора в context страницы отдельного поста.')
        self.assertEqual(
            response.context.get('post').text,
            POST_TEXT,
            'Проверьте текст в context страницы отдельного поста.')
        self.assertEqual(
            response.context.get('post').group.title,
            GROUP_TITLE,
            'Проверьте группу в context страницы отдельного поста.')
        self.assertEqual(
            response.context.get('post').image,
            'posts/small.gif',
            'Проверьте картинку в context страницы отдельного поста.')

    def test_profile_page_show_correct_context(self):
        """Проверка context шаблона profile."""
        response = self.auth_client.get(PROFILE_URL)
        self.assertEqual(
            response.context.get('page')[0].author.username,
            AUTHOR_USERNAME,
            'Проверьте автора в context страницы профайла.')
        self.assertEqual(
            response.context.get('page')[0].text,
            POST_TEXT,
            'Проверьте текст в context страницы профайла.')
        self.assertEqual(
            response.context.get('page')[0].group.title,
            GROUP_TITLE,
            'Проверьте группу в context страницы профайла.')
        self.assertEqual(
            response.context.get('page')[0].image,
            'posts/small.gif',
            'Проверьте картинку в context страницы профайла.')

    def test_auth_user_follow_author(self):
        """Проверка работы profile_follow"""
        follow_count = Follow.objects.count()
        response = self.auth_client.get(self.FOLLOW_URL)
        self.assertRedirects(
            response, PROFILE_URL, 302, 200,
            'Проверьте перенаправление после подписки на автора.')
        self.assertEqual(
           Follow.objects.count(), follow_count+1,
           'Проверьте работу profile_follow.')

    def test_auth_user_unfollow_author(self):
        """Проверка работы profile_unfollow"""
        follow_count = Follow.objects.count()
        following_user = PostViewsTests.following_user
        response = following_user.get(self.UNFOLLOW_URL)
        self.assertRedirects(
            response, PROFILE_URL, 302, 200,
            'Проверьте перенаправление после отписки автора.')
        self.assertEqual(
           Follow.objects.count(), follow_count-1,
           'Проверьте работу profile_unfollow.')

    def test_follow_index_added_post(self):
        """Проверка добавления поста на страницу follow_index подписчика."""
        post = PostViewsTests.post
        following_user = PostViewsTests.following_user
        response = following_user.get(FOLLOW_INDEX_URL)
        self.assertIn(
            post, response.context.get('page').object_list,
            'Проверьте добавление поста на страницу follow_index.')

    def test_follow_index_not_added_post(self):
        """Проверка добавления поста на страницу follow_index не подписчика."""
        post = PostViewsTests.post
        response = self.auth_client.get(FOLLOW_INDEX_URL)
        self.assertNotIn(
            post, response.context.get('page').object_list,
            'Проверьте добавление поста на страницу follow_index.')

    def test_group_added_post(self):
        """Проверка добавления поста на страницу указанной группы."""
        post = PostViewsTests.post
        response = self.guest_client.get(GROUP_URL)
        self.assertIn(
            post, response.context.get('group').posts.all(),
            'Проверьте добавление поста на страницу указанной группы.')

    def test_group_not_added_post(self):
        """Проверка добавления поста на страницу группы,
        для которой он не предназначен.
        """
        post = PostViewsTests.post
        response = self.guest_client.get(ANOTHER_GROUP_URL)
        self.assertNotIn(
            post, response.context.get('group').posts.all(),
            'Проверьте добавление поста на страницу указанной группы.')

    def test_post_delete(self):
        """Проверка удаления поста."""
        post_count = Post.objects.count()
        author = PostViewsTests.auth_author
        response = author.get(self.POST_DELETE_URL)
        self.assertRedirects(
            response, PROFILE_URL, 302, 200,
            'Проверьте перенаправление после удаления поста.')
        self.assertEqual(
           Post.objects.count(), post_count-1,
           'Проверьте работу post_delete.')

    def test_comment_delete(self):
        """Проверка удаления комментария."""
        comments_count = Comment.objects.count()
        author = PostViewsTests.following_user
        response = author.get(self.COMMENT_DELETE_URL)
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте перенаправление после удаления комментария.')
        self.assertEqual(
           Comment.objects.count(), comments_count-1,
           'Проверьте работу delete_comment.')

    def test_cache_index(self):
        """Проверка кэширования главной страницы."""
        html_0 = self.guest_client.get(INDEX_URL)
        Post.objects.create(
            text=POST_TEXT,
            author=PostViewsTests.author
        )
        html_1 = self.guest_client.get(INDEX_URL)
        self.assertHTMLEqual(
            str(html_0.content),
            str(html_1.content),
            'Проверьте работу cache главной страницы.')

    def test_cache_group(self):
        """Проверка кэширования страницы группы."""
        html_0 = self.guest_client.get(ANOTHER_GROUP_URL)
        Post.objects.create(
            text=POST_TEXT,
            author=PostViewsTests.author,
            group=PostViewsTests.another_group
        )
        html_1 = self.guest_client.get(ANOTHER_GROUP_URL)
        self.assertHTMLEqual(
            str(html_0.content),
            str(html_1.content),
            'Проверьте работу cache страницы группы.')

    def test_cache_follow_index(self):
        """Проверка кэширования страницы подписок."""
        html_0 = PostViewsTests.following_user.get(FOLLOW_INDEX_URL)
        Post.objects.create(
            text=POST_TEXT,
            author=PostViewsTests.author
        )
        html_1 = PostViewsTests.following_user.get(FOLLOW_INDEX_URL)
        self.assertHTMLEqual(
            str(html_0.content),
            str(html_1.content),
            'Проверьте работу cache страницы подписок.')


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create(username=AUTHOR_USERNAME)
        cls.user = User.objects.create(username=FOLLOWER_USERNAME)

        Follow.objects.create(user=cls.user, author=cls.author)

        cls.following_user = Client()
        cls.following_user.force_login(cls.user)

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )

        posts = [
            Post(
                text=f'{POST_TEXT} {post}',
                author=cls.author,
                group=cls.group)
            for post in range(1, 13)
        ]

        Post.objects.bulk_create(posts)

        cls.post_for_comment = Post.objects.create(
            text=POST_FOR_COMMENT_TEXT,
            author=cls.author,
            group=cls.group,
        )

        comments = [
            Comment(
                post=cls.post_for_comment,
                text=f'{COMMENT_TEXT} {comment}',
                author=cls.user)
            for comment in range(1, 9)
        ]

        Comment.objects.bulk_create(comments)

    def setUp(self):
        self.post_id = PaginatorTests.post_for_comment.id

        self.POST_URL = reverse(
            'post',
            kwargs={'username': AUTHOR_USERNAME,
                    'post_id': self.post_id})

        self.guest_client = Client()

    def test_index_first_page_containse_ten_records(self):
        """Проверка количества постов на первой странице index."""
        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(len(
            response.context.get('page').object_list), 10,
            'Количество постов на первой странице index'
            ' не совпадает с ожидаемым.')

    def test_index_second_page_containse_three_records(self):
        """Проверка количества постов на второй странице index."""
        response = self.guest_client.get(
            INDEX_URL + '?page=2')
        self.assertEqual(len(
            response.context.get('page').object_list), 3,
            'Количество постов на второй странице index'
            ' не совпадает с ожидаемым.')

    def test_group_first_page_containse_ten_records(self):
        """Проверка количества постов на первой странице group."""
        response = self.guest_client.get(GROUP_URL)
        self.assertEqual(len(
            response.context.get('page').object_list), 10,
            'Количество постов на первой странице group'
            ' не совпадает с ожидаемым.')

    def test_group_second_page_containse_three_records(self):
        """Проверка количества постов на второй странице group."""
        response = self.guest_client.get(
            GROUP_URL + '?page=2')
        self.assertEqual(len(
            response.context.get('page').object_list), 3,
            'Количество постов на второй странице group'
            ' не совпадает с ожидаемым.')

    def test_follow_index_first_page_containse_ten_records(self):
        """Проверка количества постов на первой странице follow_index."""
        response = PaginatorTests.following_user.get(FOLLOW_INDEX_URL)
        self.assertEqual(len(
            response.context.get('page').object_list), 10,
            'Количество постов на первой странице follow_index'
            ' не совпадает с ожидаемым.')

    def test_follow_index_second_page_containse_three_records(self):
        """Проверка количества постов на второй странице follow_index."""
        response = PaginatorTests.following_user.get(
            FOLLOW_INDEX_URL + '?page=2')
        self.assertEqual(len(
            response.context.get('page').object_list), 3,
            'Количество постов на второй странице follow_index'
            ' не совпадает с ожидаемым.')

    def test_post_comments_first_page_containse_five_records(self):
        """Проверка количества комментариев на первой странице post."""
        response = self.guest_client.get(self.POST_URL)
        self.assertEqual(len(
            response.context.get('page').object_list), 5,
            'Количество комментариев на первой странице post'
            ' не совпадает с ожидаемым.')

    def test_post_comments_second_page_containse_three_records(self):
        """Проверка количества комментариев на второй странице post."""
        response = self.guest_client.get(
            self.POST_URL + '?page=2')
        self.assertEqual(len(
            response.context.get('page').object_list), 3,
            'Количество комментариев на второй странице post'
            ' не совпадает с ожидаемым.')
