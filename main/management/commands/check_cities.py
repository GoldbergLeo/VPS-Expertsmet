from django.core.management.base import BaseCommand
from django.test import RequestFactory
from main.cities_config import CITIES_DATA, get_current_city_data
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Проверяет конфигурацию городов и шаблонов'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Проверка конфигурации городов...'))
        
        factory = RequestFactory()
        
        # Проверка всех городов
        for city_key, city_data in CITIES_DATA.items():
            self.stdout.write(f"\n📍 Проверка города: {city_data['name']} ({city_key})")
            
            # Проверка поддомена
            subdomain = city_data['subdomain']
            host = f"{subdomain}.expertsmet.ru"
            
            # Создаем mock request с нужным Host
            request = factory.get('/')
            request.META['HTTP_HOST'] = host
            
            # Проверяем функцию определения города
            detected_city = get_current_city_data(request)
            if detected_city['subdomain'] == subdomain:
                self.stdout.write(f"  ✅ Поддомен {host} корректно определяется")
            else:
                self.stdout.write(self.style.ERROR(f"  ❌ Поддомен {host} определяется неправильно"))
            
            # Проверка шаблона города
            template_path = f"main/city/{city_data['template_folder']}/index.html"
            full_template_path = os.path.join(settings.BASE_DIR, 'main', 'templates', template_path)
            
            if os.path.exists(full_template_path):
                self.stdout.write(f"  ✅ Шаблон {template_path} существует")
            else:
                self.stdout.write(self.style.ERROR(f"  ❌ Шаблон {template_path} НЕ НАЙДЕН"))
            
            # Проверка изображений для слайдшоу
            slideshow_dir = os.path.join(settings.BASE_DIR, 'slideshow_images', city_data['template_folder'])
            if os.path.exists(slideshow_dir):
                images_count = len([f for f in os.listdir(slideshow_dir) if f.endswith('.webp')])
                self.stdout.write(f"  ✅ Слайдшоу: найдено {images_count} изображений")
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Папка слайдшоу {slideshow_dir} не найдена"))
        
        # Проверка ALLOWED_HOSTS
        self.stdout.write(f"\n🌐 Проверка ALLOWED_HOSTS:")
        for city_key, city_data in CITIES_DATA.items():
            subdomain_host = f"{city_data['subdomain']}.expertsmet.ru"
            if subdomain_host in settings.ALLOWED_HOSTS or '.expertsmet.ru' in settings.ALLOWED_HOSTS:
                self.stdout.write(f"  ✅ {subdomain_host}")
            else:
                self.stdout.write(self.style.ERROR(f"  ❌ {subdomain_host} НЕ В ALLOWED_HOSTS"))
        
        # Проверка статических файлов
        self.stdout.write(f"\n📁 Проверка статических файлов:")
        
        static_files_to_check = [
            'main/fonts/RobotoCondensed-Regular.woff2',
            'main/img/placeholder/400x320.webp',
            'main/css/main.css',
            'main/js/main.js'
        ]
        
        for static_file in static_files_to_check:
            static_path = os.path.join(settings.BASE_DIR, 'main', 'static', static_file)
            if os.path.exists(static_path):
                self.stdout.write(f"  ✅ {static_file}")
            else:
                self.stdout.write(self.style.ERROR(f"  ❌ {static_file} НЕ НАЙДЕН"))
        
        # Проверка настроек
        self.stdout.write(f"\n⚙️  Проверка настроек:")
        self.stdout.write(f"  DEBUG: {settings.DEBUG}")
        self.stdout.write(f"  STATIC_ROOT: {settings.STATIC_ROOT}")
        self.stdout.write(f"  STATICFILES_STORAGE: {getattr(settings, 'STATICFILES_STORAGE', 'Не задан')}")
        
        # Проверка middleware
        if 'main.middleware.BlockBotsMiddleware' in settings.MIDDLEWARE:
            self.stdout.write("  ✅ BlockBotsMiddleware активен")
        else:
            self.stdout.write(self.style.ERROR("  ❌ BlockBotsMiddleware НЕ АКТИВЕН"))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Проверка завершена!'))