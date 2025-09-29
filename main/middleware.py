from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from .cities_config import get_current_city_data, city_exists_in_config, get_city_key_by_subdomain
from .views import city_view

class BlockBotsMiddleware:
    """Middleware для блокировки WordPress ботов и подозрительных запросов"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Список подозрительных путей
        self.blocked_paths = [
            '/wp-',
            '/wordpress',
            '/xmlrpc.php',
            '.php',
            '.asp',
            '.aspx',
            '.jsp'
        ]
        
    def __call__(self, request):
        # Проверяем путь запроса
        path = request.path.lower()
        
        # Блокируем WordPress запросы
        if any(blocked in path for blocked in self.blocked_paths):
            return HttpResponse(status=444)  # 444 - закрываем соединение
            
        return self.get_response(request)


class SubdomainMiddleware:
    """Middleware для автоматического определения поддомена и показа городского контента"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        try:
            # Получаем заголовок Host
            host = request.META.get('HTTP_HOST', '')
            
            # Если это локальный хост или тестовый сервер, пропускаем
            if (host.startswith('127.0.0.1') or 
                host.startswith('localhost') or 
                host == 'testserver' or
                not host):
                return self.get_response(request)
            
            # Извлекаем поддомен
            if '.' in host:
                subdomain = host.split('.')[0]
            else:
                subdomain = None
            
            # Проверяем, является ли поддомен городом
            if subdomain and city_exists_in_config(subdomain):
                # Если это корневой путь и поддомен города, показываем городской контент
                if request.path == '/':
                    # Вместо перенаправления, сразу вызываем city_view с каноническим ключом города
                    city_key = get_city_key_by_subdomain(subdomain)
                    return city_view(request, city_key or subdomain)
            
            return self.get_response(request)
            
        except Exception as e:
            # В случае ошибки просто пропускаем запрос
            return self.get_response(request)
