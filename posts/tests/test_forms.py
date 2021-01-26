import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

AUTHOR_USERNAME = 'PostTestUser'
AUTH_USER_USERNAME = 'TestUser'

GROUP_TITLE = 'Тестовая группа'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-group'

POST_TEXT = 'Тестовый текст'
POST_TEXT_UPD = 'Тестовый текст изменён'
POST_IMAGE = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

COMMENT_TEXT = 'Тестовый комментарий'

INDEX_URL = reverse('index')
GROUP_URL = reverse('group', kwargs={'slug': GROUP_SLUG})
NEW_POST_URL = reverse('new_post')

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create(username=AUTHOR_USERNAME)

        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create(username=AUTH_USER_USERNAME)
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

        self.post_id = PostCreateFormTests.post.id

        self.POST_EDIT_URL = reverse(
            'post_edit',
            kwargs={'username': AUTHOR_USERNAME,
                    'post_id': self.post_id}
        )
        self.POST_URL = reverse(
            'post',
            kwargs={'username': AUTHOR_USERNAME,
                    'post_id': self.post_id}
        )
        self.ADD_COMMENT_URL = reverse(
            'add_comment',
            kwargs={'username': AUTHOR_USERNAME,
                    'post_id': self.post_id}
        )

    def test_redirect_create_form_new_post(self):
        """Проверка добавления формы new_post."""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=POST_IMAGE,
            content_type='image/gif'
        )
        form_data = {
            'text': POST_TEXT,
            'author': self.auth_client,
            'image': uploaded
        }
        response = self.auth_client.post(
            NEW_POST_URL, data=form_data, follow=True)
        self.assertEqual(
            Post.objects.count(),
            post_count+1,
            'Проверьте добавление поста, после отправки формы new_post.')
        self.assertRedirects(
            response, INDEX_URL, 302, 200,
            'Проверьте перенаправление после заполнения формы new_post.')

    def test_redirect_create_form_post_edit(self):
        """Проверка добавления формы post_edit."""
        post_count = Post.objects.count()
        author = PostCreateFormTests.auth_author
        form_data_edited = {
            'text': POST_TEXT_UPD
        }
        response = author.post(
            self.POST_EDIT_URL, data=form_data_edited, follow=True)
        self.assertEqual(
            response.context.get('post').text,
            form_data_edited['text'],
            'Проверьте изменение поста, после отправки формы post_edit.')
        self.assertEqual(
           Post.objects.count(),
           post_count,
           'Проверьте изменение поста, после отправки формы post_edit.')
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте перенаправление после заполнения формы post_edit.')

    def test_redirect_create_form_add_comment(self):
        """Проверка добавления формы add_comment."""
        comments_count = Comment.objects.count()
        form_data = {
            'post': PostCreateFormTests.post,
            'author': self.auth_client,
            'text': COMMENT_TEXT
        }
        response = self.auth_client.post(
            self.ADD_COMMENT_URL, data=form_data, follow=True)
        self.assertEqual(
            response.context.get('comments')[0].text,
            form_data['text'],
            'Проверьте комментарий, после отправки формы add_comment.')
        self.assertEqual(
            Comment.objects.count(),
            comments_count+1,
            'Проверьте комментарий, после отправки формы add_comment.')
        self.assertRedirects(
            response, self.POST_URL, 302, 200,
            'Проверьте перенаправляете ли, вы пользователя'
            'после отправки формы с add_comment на post.')
