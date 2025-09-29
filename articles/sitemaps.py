from django.contrib.sitemaps import Sitemap
from articles.models import Articles
from main.cities_config import CITIES_DATA

class ArticlesSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Articles.objects.all().order_by('-data')

    def lastmod(self, obj):
        return obj.data

    def location(self, obj):
        return obj.get_absolute_url()

class RegionalArticlesSitemap(Sitemap):
    """Sitemap для региональных версий статей"""
    changefreq = "daily"
    priority = 0.6

    def items(self):
        articles = Articles.objects.all().order_by('-data')
        regional_items = []
        
        for article in articles:
            for city_key, city_data in CITIES_DATA.items():
                if not city_data.get('is_main', False):  # Безопасная проверка
                    regional_items.append({
                        'article': article,
                        'city': city_data
                    })
        
        return regional_items

    def lastmod(self, obj):
        return obj['article'].data

    def location(self, obj):
        try:
            city_url = obj['city']['url']
            article_url = obj['article'].get_absolute_url()
            # Убираем дублирование слэшей
            if city_url.endswith('/') and article_url.startswith('/'):
                return f"{city_url.rstrip('/')}{article_url}"
            return f"{city_url}{article_url}"
        except (KeyError, AttributeError):
            # Fallback в случае ошибки
            return obj['article'].get_absolute_url()
