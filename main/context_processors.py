# Контекст-процессоры для добавления данных во все шаблоны
from .cities_config import get_current_city_data, get_all_cities


def cities_context(request):
    """
    Добавляет информацию о городах в контекст всех шаблонов
    
    Доступные переменные в шаблонах:
    - current_city: данные текущего города
    - all_cities: список всех городов для модального окна
    """
    current_city = get_current_city_data(request)
    all_cities = get_all_cities()
    
    return {
        'current_city': current_city,
        'all_cities': all_cities,
    }