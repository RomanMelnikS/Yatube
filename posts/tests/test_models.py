from django.test import TestCase

from posts.models import Comment, Group, Post, User

AUTHOR_USERNAME = 'PostTestUser'

GROUP_TITLE = 'Тестовая группа'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-group'

FIELD_POST_VERBOSES = {
    'text': 'Ваша запись',
    'pub_date': 'Дата публикации',
    'author': 'Автор',
    'group': 'Группа',
}
FIELD_GROUP_VERBOSES = {
    'title': 'Название группы',
    'slug': 'URL группы',
    'description': 'Описание группы'
}
FIELD_POST_HELP_TEXTS = {
    'text': 'Поделитесь своими мыслями с сообществом.',
    'group': 'К какой группе относится ваша запись?'
}
FIELD_GROUP_HELP_TEXTS = {
    'title': 'Дайте понятное название группе.',
    'slug': 'Придумайте URL группы или оставьте предложенный.',
    'description': 'Опишите, какие записи, должны попасть в группу.'
}
FIELD_COMMENT_VERBOSES = {
    'post': 'Комментируемый пост',
    'author': 'Автор комментария',
    'text': 'Текст комментария',
    'created': 'Дата и время публикации'
}

POST_TEXT = 'Длинный тестовый текст, больше 15 символов'

COMMENT_TEXT = 'Длинный текст комментария, больше 15 символов'


class PostModelTest(TestCase):
    def setUp(self):
        self.author = User.objects.create(username=AUTHOR_USERNAME)

        self.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )

        self.post = Post.objects.create(
            text=POST_TEXT,
            author=self.author,
            group=self.group
        )

        self.comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            text=COMMENT_TEXT,
        )

    def test_post_verbose_name(self):
        """Провека verbose_name в полях Post."""
        for value, expected in FIELD_POST_VERBOSES.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name,
                    expected,
                    'verbose_name в полях Post не совпадает с ожидаемым.')

    def test_group_verbose_name(self):
        """Проверка verbose_name в полях Group."""
        for value, expected in FIELD_GROUP_VERBOSES.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.group._meta.get_field(value).verbose_name,
                    expected,
                    'verbose_name в полях Group не совпадает с ожидаемым.')

    def test_post_help_text(self):
        """Проверка help_text в полях Post."""
        for value, expected in FIELD_POST_HELP_TEXTS.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text,
                    expected,
                    'help_text в полях Post не совпадает с ожидаемым.')

    def test_group_help_text(self):
        """Проверка help_text в полях Group."""
        for value, expected in FIELD_GROUP_HELP_TEXTS.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.group._meta.get_field(value).help_text,
                    expected,
                    'help_text в полях Group не совпадает с ожидаемым.')

    def test_comment_verbose_name(self):
        """Проверка verbose_name в полях Comment."""
        for value, expected in FIELD_COMMENT_VERBOSES.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.comment._meta.get_field(value).verbose_name,
                    expected,
                    'verbose_name в полях Comment не совпадает с ожидаемым.')

    def test_comment_object_name(self):
        """Проверка поля __str__ в классе Comment."""
        expected_comment_object_name = self.comment.text[:15]
        self.assertEquals(
            expected_comment_object_name,
            str(self.comment),
            'Поле __str__ в классе Comment не совпадает с ожидаемым.')

    def test_post_object_name(self):
        """Проверка поля __str__ в классе Post."""
        expected_post_object_name = self.post.text[:15]
        self.assertEquals(
            expected_post_object_name,
            str(self.post),
            'Поле __str__ в классе Post не совпадает с ожидаемым.')

    def test_group_object_name(self):
        """Проверка поля __str__ в классе Group."""
        expected_group_object_name = self.group.title
        self.assertEquals(
            expected_group_object_name,
            str(self.group),
            'Поле __str__ в классе Group не совпадает с ожидаемым.')
