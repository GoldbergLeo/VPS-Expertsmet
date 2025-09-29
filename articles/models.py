from django.db import models
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image
from io import BytesIO
import os
import posixpath


def _posix_join(*parts: str) -> str:
    """Join path fragments using POSIX separators regardless of platform."""
    cleaned = [segment.strip('/') for segment in parts if segment]
    return '/'.join(cleaned)

class Articles(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Ссылка', max_length=200, unique=True, blank=True)
    discr = models.CharField('Описание', max_length=250, blank=True)
    data = models.DateField('Дата публикаций')
    full_text = models.TextField('Статья')
    image = models.ImageField('Изображение', upload_to='img/articles/', blank=True, null=True)
    
    # Поля для SEO
    meta_title = models.CharField('Meta Title', max_length=75, blank=True, help_text="Заголовок для SEO")
    meta_description = models.CharField('Meta Description', max_length=180, blank=True, help_text="Описание для SEO")
    meta_keywords = models.CharField('Meta Keywords', max_length=250, blank=True, help_text="Ключевые слова для SEO")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Генерация slug, если он не задан
        if not self.slug:
            base_slug = slugify(self.title)
            slug_candidate = base_slug
            counter = 1
            while Articles.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate

        # Заполнение незаполненных полей
        if not self.discr:
            self.discr = self.full_text[:250]
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.discr

        # Сохраняем модель первично, чтобы у поля image появился путь на диске
        super().save(*args, **kwargs)

        if not self.image:
            return

        try:
            self._normalize_image_path()
            self._convert_image_to_webp()
        except Exception as exc:  # pragma: no cover - неверные данные не должны рушить сохранение
            print(f"❌ Ошибка обработки изображения {self.image.name}: {exc}")

    def get_absolute_url(self):
        from django.urls import reverse
        try:
            if self.slug:
                return reverse("news_detail", kwargs={"slug": self.slug})
            else:
                # Если slug пустой, возвращаем URL списка статей
                return reverse("articles_list")
        except:
            # Если URL не найден, возвращаем список статей
            return reverse("articles_list")

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    # --- Вспомогательные методы -------------------------------------------------

    def _normalize_image_path(self):
        """Убираем дублирующиеся сегменты вида img/articles/img/articles/ из пути."""
        storage = self.image.storage
        current_name = self.image.name or ''
        if not current_name:
            return

        normalized = current_name.replace('\\', '/')
        duplicated = 'img/articles/'
        pattern = duplicated + duplicated

        while pattern in normalized:
            normalized = normalized.replace(pattern, duplicated)

        if normalized == current_name:
            return

        if not storage.exists(current_name):
            self.image.name = normalized
            self.__class__.objects.filter(pk=self.pk).update(image=normalized)
            return

        with storage.open(current_name, 'rb') as original:
            content = ContentFile(original.read())

        storage.save(normalized, content)
        storage.delete(current_name)
        self.image.name = normalized
        self.__class__.objects.filter(pk=self.pk).update(image=normalized)

    def _convert_image_to_webp(self):
        """Конвертирует изображение в WebP, если это JPG/PNG и ещё не конвертировано."""
        storage = self.image.storage
        current_name = (self.image.name or '').replace('\\', '/')
        if not current_name:
            return

        _, ext = os.path.splitext(current_name)
        if ext.lower() not in {'.png', '.jpg', '.jpeg'}:
            return

        if not storage.exists(current_name):
            return

        with storage.open(current_name, 'rb') as image_file:
            with Image.open(image_file) as img:
                output = BytesIO()
                img.save(output, format='WEBP', quality=90)
        output.seek(0)

        directory = os.path.dirname(current_name)
        base_name = os.path.splitext(os.path.basename(current_name))[0]
        new_rel_path = _posix_join(directory, f"{base_name}.webp") if directory else f"{base_name}.webp"

        if storage.exists(new_rel_path):
            storage.delete(new_rel_path)

        storage.save(new_rel_path, ContentFile(output.read()))
        storage.delete(current_name)

        self.image.name = new_rel_path
        self.__class__.objects.filter(pk=self.pk).update(image=new_rel_path)

    def image_exists(self):
        if not self.image:
            return False
        name = self.image.name or ''
        if not name:
            return False
        try:
            return self.image.storage.exists(name)
        except Exception:
            return False

    @property
    def safe_image_url(self):
        if self.image_exists():
            return self.image.url
        return ''

    @property
    def placeholder_image_url(self):
        """Return site-wide placeholder for article cards when no upload exists."""
        return self.get_placeholder_image_url()

    @property
    def display_image_url(self):
        """Expose either the uploaded image or fallback placeholder."""
        return self.safe_image_url or self.placeholder_image_url

    @classmethod
    def get_placeholder_image_url(cls):
        placeholder_path = 'img/articles/_gp138n1u271zx47vyqkn_0_RcZoOwY.webp'
        media_prefix = settings.MEDIA_URL or '/media/'
        if not media_prefix.endswith('/'):
            media_prefix = f"{media_prefix}/"
        return f"{media_prefix}{placeholder_path}"
