from django.core.management.base import BaseCommand
from main.models import Article  # Если модель называется Article

class Command(BaseCommand):
    help = "Обновляет все существующие записи модели Article, чтобы применить новую логику в методе save()"

    def handle(self, *args, **options):
        articles = Article.objects.all()
        count = articles.count()
        self.stdout.write(f"Найдено {count} записей для обновления.")

        for article in articles:
            # Если необходимо, можно добавить проверку: например, обновлять только записи без webp
            article.save()
            self.stdout.write(f"Запись '{article.title}' обновлена.")

        self.stdout.write(self.style.SUCCESS("Обновление завершено."))
