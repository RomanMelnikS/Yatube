from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Ваша запись',
        help_text='Поделитесь своими мыслями с сообществом.')

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts', verbose_name='Автор')

    group = models.ForeignKey(
        'Group', models.SET_NULL,
        blank=True, null=True, related_name='posts',
        verbose_name='Группа',
        help_text='К какой группе относится ваша запись?')

    image = models.ImageField(
        upload_to='posts/',
        verbose_name='Картинка',
        help_text='Добавьте картинку в дополнение к записи.',
        blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название группы',
        help_text='Дайте понятное название группе.',
        max_length=200, unique=True)

    slug = models.SlugField(
        verbose_name='URL группы',
        help_text='Придумайте URL группы или оставьте предложенный.',
        max_length=250, unique=True)

    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Опишите, какие записи, должны попасть в группу.')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемый пост')

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')

    text = models.TextField(
        verbose_name='Текст комментария')

    created = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following', null=True,
        verbose_name='Following'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
