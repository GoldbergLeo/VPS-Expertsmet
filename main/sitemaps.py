from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from main.cities_config import CITIES_DATA

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        # Список URL-имен для статичных страниц
        return ['index', 'about', 'contacts', 'services', 'projects', 'calculator']

    def location(self, item):
        return reverse(item)

class CitySitemap(Sitemap):
    """Sitemap для городских страниц"""
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        # Возвращаем все города
        return list(CITIES_DATA.keys())

    def location(self, item):
        # URL для городской страницы
        city_data = CITIES_DATA.get(item)
        if not city_data:
            return "https://expertsmet.ru/"
        return f"{city_data['url'].rstrip('/')}/"

    def lastmod(self, item):
        # Можно добавить логику для определения последнего обновления
        from django.utils import timezone
        return timezone.now()

class RegionalSitemap(Sitemap):
    """Sitemap для региональных версий основных страниц"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # Создаем комбинации городов и страниц
        cities = [city for city in CITIES_DATA.keys() if not CITIES_DATA[city]['is_main']]
        pages = ['about', 'services', 'projects', 'calculator']
        
        items = []
        for city in cities:
            for page in pages:
                items.append({
                    'city': city,
                    'page': page
                })
        return items

    def location(self, item):
        # URL для региональной страницы
        city_data = CITIES_DATA.get(item['city'])
        if not city_data:
            return f"https://expertsmet.ru/{item['page'].strip('/')}/"
        base = city_data['url'].rstrip('/')
        page = item['page'].strip('/')
        return f"{base}/{page}/"

    def lastmod(self, item):
        from django.utils import timezone
        return timezone.now()
