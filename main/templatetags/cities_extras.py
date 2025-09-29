from django import template
from main.cities_config import get_current_city_data, get_all_cities

register = template.Library()

@register.inclusion_tag('main/partials/city_selector.html', takes_context=True)
def city_selector(context):
    """Отображает селектор городов"""
    request = context['request']
    current_city = get_current_city_data(request)
    all_cities = get_all_cities()
    
    return {
        'current_city': current_city,
        'all_cities': all_cities,
        'request': request
    }

@register.simple_tag(takes_context=True)
def get_city_data(context):
    """Получает данные текущего города"""
    request = context['request']
    return get_current_city_data(request)

@register.filter
def city_phone_format(phone):
    """Форматирует телефон для города"""
    if not phone:
        return '+7 (800) 300-87-72'
    return phone

@register.simple_tag
def city_canonical_url(city_data):
    """Генерирует канонический URL для города"""
    if city_data:
        return city_data.get('url', 'https://expertsmet.ru/')
    return 'https://expertsmet.ru/'