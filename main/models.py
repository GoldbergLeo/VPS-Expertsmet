from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, max_length=200, verbose_name='URL-метка', blank=True)
    content = models.TextField(verbose_name='Содержимое статьи')
    published_date = models.DateField(verbose_name='Дата публикации')
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='Изображение')
    # при желании можно добавить поле "описание" (description) для <meta>

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Генерируем slug на основе заголовка, если slug не заполнен.
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
    


class Subscription(models.Model):
    email = models.EmailField('Email подписчика', unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email