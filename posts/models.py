from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Ваша запись',
        help_text='Поделитесь своими мыслями с сообществом.')

    pub_date = models.DateTimeField(
        'date published', auto_now_add=True)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts', verbose_name='Автор')

    group = models.ForeignKey(
        'Group', models.SET_NULL,
        blank=True, null=True, related_name='posts',
        verbose_name='Группа',
        help_text='К какой группе относится ваша запись?')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return self.text


class Group(models.Model):
    title = models.CharField(
        max_length=200, unique=True)

    slug = models.SlugField(
        max_length=250, unique=True)

    description = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
