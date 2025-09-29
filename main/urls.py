from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.templatetags.static import static as static_url
from .views import (
    index, services, projects, calculator, about, contacts,
    send_form_email, subscribe, thank_you, robots_txt, city_view, quick_contact, health_check,
    favicon_view, placeholder_image,
)
from django.shortcuts import render

urlpatterns = [
    path("", index, name="index"),
    path("services/", services, name="services"),
    path("projects/", projects, name="projects"),
    path("calculator/", calculator, name="calculator"),
    path("about/", about, name="about"),
    path("contacts/", contacts, name="contacts"),
    path("send-form/", send_form_email, name="send_form_email"),
    path("subscribe/", subscribe, name="subscribe"),
    path("quick-contact/", quick_contact, name="quick_contact"),
    path("thank-you/", thank_you, name="thank-you"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("api/placeholder/<int:w>/<int:h>", placeholder_image, name="placeholder_image"),
    path(".well-known/traffic-advice", lambda request: HttpResponse("", status=204), name="traffic_advice"),
    path("health/", health_check, name="health_check"),
    path("test-forms/", lambda request: render(request, 'main/test_forms.html'), name="test_forms"),
    path("simple-test-forms/", lambda request: render(request, 'main/simple_test_forms.html'), name="simple_test_forms"),
    
    # Favicon (динамический для городов)
    path("favicon.ico", favicon_view, name="favicon"),
    path("favicon.svg", RedirectView.as_view(url=static_url('favicon-120.png'), permanent=True)),
    path("favicon-120.png", RedirectView.as_view(url=static_url('favicon-120.png'), permanent=True)),
    path("favicon-32x32.png", RedirectView.as_view(url=static_url('favicon-120.png'), permanent=True)),
    path("favicon-16x16.png", RedirectView.as_view(url=static_url('favicon-120.png'), permanent=True)),
    
    # Тестовая страница для отладки
    path("test/", lambda request: city_view(request, 'moscow'), name="test_moscow"),
    
    # Маршруты для городов (должны быть в конце)
    path("city/<str:city_slug>/", city_view, name="city"),
]

# Добавляем статические файлы для разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
