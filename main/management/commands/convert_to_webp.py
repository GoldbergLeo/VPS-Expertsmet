from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from articles.models import Articles
from PIL import Image
from io import BytesIO
import os
import posixpath

class Command(BaseCommand):
    help = "Конвертирует изображения статей в формат WEBP без дублирования путей"

    def handle(self, *args, **options):
        articles = Articles.objects.exclude(image='').exclude(image__isnull=True)
        total = articles.count()
        self.stdout.write(f"🔍 Найдено {total} записей для обработки.")

        for article in articles:
            ext = os.path.splitext(article.image.name)[1].lower()
            image_path = article.image.path

            # Проверяем, что изображение существует на диске
            if not os.path.exists(image_path):
                self.stdout.write(self.style.ERROR(f"❌ Файл отсутствует: {image_path}"))
                continue

            normalized_name = article.image.name.replace('\\', '/')
            duplicated = 'img/articles/'
            pattern = duplicated + duplicated
            while pattern in normalized_name:
                normalized_name = normalized_name.replace(pattern, duplicated)

            if normalized_name != article.image.name:
                storage = article.image.storage
                with storage.open(article.image.name, 'rb') as original:
                    storage.save(normalized_name, ContentFile(original.read()))
                storage.delete(article.image.name)
                article.image.name = normalized_name
                article.__class__.objects.filter(pk=article.pk).update(image=normalized_name)
                image_path = article.image.path
                ext = os.path.splitext(article.image.name)[1].lower()

            if ext not in ['.png', '.jpg', '.jpeg']:
                self.stdout.write(self.style.WARNING(f"⏭️ [SKIP] {article.title}: формат {ext} не требует конвертации"))
                continue

            try:
                with Image.open(image_path) as img:
                    output = BytesIO()
                    img.save(output, format='WEBP', quality=90)
                output.seek(0)

                directory = os.path.dirname(article.image.name)
                base_name = os.path.splitext(os.path.basename(article.image.name))[0]
                new_rel_path = posixpath.join(directory, f"{base_name}.webp") if directory else f"{base_name}.webp"

                storage = article.image.storage
                if storage.exists(new_rel_path):
                    storage.delete(new_rel_path)

                storage.save(new_rel_path, ContentFile(output.read()))
                storage.delete(article.image.name)

                article.image.name = new_rel_path
                article.__class__.objects.filter(pk=article.pk).update(image=new_rel_path)

                self.stdout.write(self.style.SUCCESS(f"✅ {article.title}: конвертировано в WebP ({new_rel_path})"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ [ERROR] {article.title}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Конвертация завершена."))
