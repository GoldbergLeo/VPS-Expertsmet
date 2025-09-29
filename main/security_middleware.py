"""
Middleware для защиты форм от атак
"""
import time
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import PermissionDenied

class FormSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверяем только POST запросы к формам
        if request.method == 'POST' and self._is_form_request(request):
            if not self._check_form_security(request):
                return HttpResponseForbidden("Слишком много запросов. Попробуйте позже.")
        
        response = self.get_response(request)
        return response
    
    def _is_form_request(self, request):
        """Проверяем, является ли запрос отправкой формы"""
        form_urls = [
            '/send-form/',
            '/subscribe/',
            '/quick-contact/',
            '/calculator/',
        ]
        return any(request.path.endswith(url) for url in form_urls)
    
    def _check_form_security(self, request):
        """Проверяем безопасность формы"""
        # Получаем IP адрес
        ip = self._get_client_ip(request)
        
        # Ключ для кэша
        cache_key = f"form_attempts_{ip}"
        
        # Получаем текущие попытки
        attempts = cache.get(cache_key, 0)
        
        # Проверяем лимит
        max_attempts = getattr(settings, 'MAX_FORM_ATTEMPTS', 10)
        lockout_time = getattr(settings, 'FORM_LOCKOUT_TIME', 300)  # 5 минут
        
        if attempts >= max_attempts:
            # Проверяем, не истекло ли время блокировки
            lockout_key = f"form_lockout_{ip}"
            if cache.get(lockout_key):
                return False
            else:
                # Сбрасываем счетчик
                cache.delete(cache_key)
                attempts = 0
        
        # Увеличиваем счетчик попыток
        attempts += 1
        cache.set(cache_key, attempts, 60)  # Храним 1 минуту
        
        # Если превышен лимит, блокируем
        if attempts >= max_attempts:
            cache.set(lockout_key, True, lockout_time)
            return False
        
        return True
    
    def _get_client_ip(self, request):
        """Получаем реальный IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RateLimitMiddleware:
    """Middleware для ограничения частоты запросов"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверяем только POST запросы
        if request.method == 'POST':
            if not self._check_rate_limit(request):
                return HttpResponseForbidden("Слишком частые запросы. Подождите немного.")
        
        response = self.get_response(request)
        return response
    
    def _check_rate_limit(self, request):
        """Проверяем ограничение частоты запросов"""
        ip = self._get_client_ip(request)
        cache_key = f"rate_limit_{ip}"
        
        # Получаем текущее время
        current_time = time.time()
        
        # Получаем историю запросов
        requests = cache.get(cache_key, [])
        
        # Убираем старые запросы (старше 1 минуты)
        requests = [req_time for req_time in requests if current_time - req_time < 60]
        
        # Проверяем лимит (максимум 30 запросов в минуту)
        max_requests = 30
        if len(requests) >= max_requests:
            return False
        
        # Добавляем текущий запрос
        requests.append(current_time)
        cache.set(cache_key, requests, 60)
        
        return True
    
    def _get_client_ip(self, request):
        """Получаем реальный IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
