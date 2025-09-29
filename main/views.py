from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap as django_sitemap
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.contrib import messages
from django.utils.html import strip_tags
import logging
from articles.models import Articles  # Модель статей
from articles.sitemaps import ArticlesSitemap, RegionalArticlesSitemap
from main.sitemaps import StaticViewSitemap, CitySitemap, RegionalSitemap
from .cities_config import (
    get_current_city_data,
    get_city_template_path,
    get_city_by_key,
    get_city_by_subdomain,
    get_city_key_by_subdomain,
)
import os
from django.templatetags.static import static

# Настройка логирования
logger = logging.getLogger(__name__)

CITY_SITEMAP_STATIC_PATHS = [
    "",
    "about",
    "services",
    "projects",
    "calculator",
    "contacts",
    "articles",
]


class CityStaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def __init__(self, city_data):
        self.city_data = city_data

    def items(self):
        return CITY_SITEMAP_STATIC_PATHS

    def location(self, item):
        # Возвращаем только относительный URL, Django sitemap автоматически добавит домен
        if not item:
            return "/"
        return f"/{item.strip('/')}/"
    
    def get_urls(self, page=1, site=None, protocol=None):
        """Переопределяем для установки правильного домена"""
        urls = []
        for item in self.paginator.page(page).object_list:
            loc = self.location(item)
            # Устанавливаем правильный домен для города
            if not loc.startswith('http'):
                loc = f"{self.city_data['url']}{loc}"
            urls.append({
                'location': loc,
                'lastmod': self.lastmod(item),
                'changefreq': self.changefreq,
                'priority': self.priority,
            })
        return urls


class CityArticlesSitemap(ArticlesSitemap):
    priority = 0.6

    def __init__(self, city_data):
        super().__init__()
        self.city_data = city_data

    def location(self, obj):
        # Возвращаем только относительный URL, Django sitemap автоматически добавит домен
        return obj.get_absolute_url()
    
    def get_urls(self, page=1, site=None, protocol=None):
        """Переопределяем для установки правильного домена"""
        urls = []
        for item in self.paginator.page(page).object_list:
            loc = self.location(item)
            # Устанавливаем правильный домен для города
            if not loc.startswith('http'):
                loc = f"{self.city_data['url']}{loc}"
            urls.append({
                'location': loc,
                'lastmod': self.lastmod(item),
                'changefreq': self.changefreq,
                'priority': self.priority,
            })
        return urls


GLOBAL_SITEMAPS = {
    'static': StaticViewSitemap,
    'cities': CitySitemap,
    'regional': RegionalSitemap,
    'articles': ArticlesSitemap,
    'regional_articles': RegionalArticlesSitemap,
}

def index(request):
    # Главная страница - без городских данных
    # Получаем последние 6 статей, сортируя по дате в обратном порядке
    last_articles = Articles.objects.order_by('-data')[:6]
    
    context = {
        'title': 'Составление сметной документации – разработка и проверка смет | Expertsmet',
        'meta_description': 'Профессиональное составление и разработка сметной документации по всей России. Стоимость сметы, услуги сметчика, проверка и анализ смет. Expertsmet - работаем по всей России',
        'meta_keywords': 'оформление сметной документации, разработать смету, разработать проектно сметную документацию, выполнение проектно сметной документации, стоимость разработки сметной документации, составить смету онлайн, экспертиза проектно сметной документации, составить смету цена, изготовление сметной документации, стоимость подготовки сметной документации, составление сметной документации цена, стоимость проверки сметной документации',
        'last_articles': last_articles,
        # current_city не передаем для главной страницы
    }
    
    return render(request, 'main/index.html', context)

def _static_file_exists(rel_path):
    """Проверка наличия статического файла как в STATIC_ROOT, так и в STATICFILES_DIRS."""
    try:
        from django.conf import settings
        # Проверяем STATIC_ROOT
        if settings.STATIC_ROOT:
            candidate = os.path.join(settings.STATIC_ROOT, rel_path)
            if os.path.exists(candidate):
                return True
        # Проверяем STATICFILES_DIRS
        for base in getattr(settings, 'STATICFILES_DIRS', []):
            candidate = os.path.join(base, rel_path)
            if os.path.exists(candidate):
                return True
    except Exception:
        pass
    return False

def favicon_view(request):
    """Отдаёт favicon per-city, если такой существует, иначе дефолт."""
    from django.conf import settings
    from .cities_config import CITIES_DATA

    # Единый фавикон для всех страниц
    return HttpResponseRedirect(static('favicon-120.png'))

def placeholder_image(request, w: int, h: int):
    """Простой плейсхолдер как SVG, чтобы не было 404 в логах."""
    try:
        w = max(1, min(int(w), 4000))
        h = max(1, min(int(h), 4000))
    except Exception:
        w, h = 400, 320

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">
  <rect width="100%" height="100%" fill="#f0f0f0"/>
  <rect x="1" y="1" width="{w-2}" height="{h-2}" fill="none" stroke="#ddd"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        font-family="Arial, sans-serif" font-size="{max(10, min(w,h)//10)}" fill="#999">
    {w}×{h}
  </text>
  <text x="50%" y="{h-10}" dominant-baseline="middle" text-anchor="middle"
        font-family="Arial, sans-serif" font-size="10" fill="#bbb">
    placeholder
  </text>
  </svg>'''
    resp = HttpResponse(svg, content_type="image/svg+xml; charset=utf-8")
    resp["Cache-Control"] = "public, max-age=86400"
    return resp
def city_view(request, city_slug):
    """
    Отображение страницы конкретного города
    """
    from .cities_config import CITIES_DATA
    
    # Получаем данные города по slug
    city_data = get_city_by_key(city_slug)
    
    if not city_data:
        # Если город не найден, возвращаем 404
        return HttpResponse("Город не найден", status=404)
    
    # Получаем последние 6 статей
    last_articles = Articles.objects.order_by('-data')[:6]
    
    # Определяем шаблон для города
    city_template = get_city_template_path(city_data)
    
    # Проверяем существование шаблона города
    template_path = os.path.join(settings.BASE_DIR, 'main', 'templates', city_template)
    
    if os.path.exists(template_path):
        template_name = city_template
    else:
        # Если шаблон города не найден, используем базовый шаблон
        template_name = 'main/city_base.html'
    
    # Динамические метаданные для города
    city_name = city_data['name']
    
    context = {
        'title': f'Услуги по разработке строительной документации {city_name} | EXPERTsmet',
        'meta_description': f'EXPERTsmet - профессиональная разработка сметной документации в {city_name}. Работаем по ФСНБ-2022, ФЕР, ТЕР. Гарантируем прохождение экспертизы. {city_data["phone"]}',
        'meta_keywords': f'разработка строительной документации {city_name}, сметная документация {city_name}, смета {city_name}, экспертиза сметы {city_name}, строительные сметы {city_name}',
        'last_articles': last_articles,
        'current_city': city_data,
    }
    
    return render(request, template_name, context)

def services(request):
    return render(request, 'main/services.html')

def projects(request):
    return render(request, 'main/projects.html')

def calculator(request):
    from .forms import CalculatorForm
    
    if request.method == 'POST':
        form = CalculatorForm(request.POST)
        if form.is_valid():
            try:
                # Получаем данные формы
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']
                project_type = form.cleaned_data['project_type']
                area = form.cleaned_data['area']
                complexity = form.cleaned_data['complexity']
                services = form.cleaned_data['services']
                urgency = form.cleaned_data['urgency']
                additional_info = form.cleaned_data['additional_info']
                estimated_cost = form.cleaned_data.get('estimated_cost', 0)
                
                # Проверяем, что email адрес валиден и не является тестовым
                if not email or 'example.com' in email or 'test' in email:
                    logger.warning(f"Попытка отправки калькулятора с тестовым email: {email}")
                    messages.warning(request, 'Заявка отправлена администратору, но подтверждение не отправлено (тестовый email).')
                    # Продолжаем отправку администратору, но не отправляем клиенту
                    send_to_client = False
                else:
                    send_to_client = True
                
                # Получаем человекочитаемые названия
                project_type_display = dict(form.fields['project_type'].choices)[project_type]
                complexity_display = dict(form.fields['complexity'].choices)[complexity]
                urgency_display = dict(form.fields['urgency'].choices)[urgency]
                services_display = [dict(form.fields['services'].choices)[service] for service in services]
                
                # Создаем HTML email
                body_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                        .section {{ margin: 20px 0; }}
                        .field {{ margin: 10px 0; }}
                        .field-label {{ font-weight: bold; color: #495057; }}
                        .field-value {{ margin-left: 10px; }}
                        .services-list {{ margin-left: 20px; }}
                        .cost {{ font-size: 18px; font-weight: bold; color: #28a745; }}
                        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>🚧 Новая заявка на расчет сметы с сайта Expertsmet</h2>
                    </div>
                    
                    <div class="section">
                        <h3>👤 Контактная информация</h3>
                        <div class="field">
                            <span class="field-label">Имя:</span>
                            <span class="field-value">{name}</span>
                        </div>
                        <div class="field">
                            <span class="field-label">Email:</span>
                            <span class="field-value">{email}</span>
                        </div>
                        <div class="field">
                            <span class="field-label">Телефон:</span>
                            <span class="field-value">{phone or 'Не указан'}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>🏗️ Параметры проекта</h3>
                        <div class="field">
                            <span class="field-label">Тип проекта:</span>
                            <span class="field-value">{project_type_display}</span>
                        </div>
                        <div class="field">
                            <span class="field-label">Площадь:</span>
                            <span class="field-value">{area} м²</span>
                        </div>
                        <div class="field">
                            <span class="field-label">Сложность:</span>
                            <span class="field-value">{complexity_display}</span>
                        </div>
                        <div class="field">
                            <span class="field-label">Срочность:</span>
                            <span class="field-value">{urgency_display}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>🔧 Требуемые услуги</h3>
                        <div class="services-list">
                            {''.join([f'<div>• {service}</div>' for service in services_display])}
                        </div>
                    </div>
                    
                    {f'<div class="section"><h3>💰 Расчетная стоимость</h3><div class="cost">{estimated_cost:,.0f} ₽</div></div>' if estimated_cost else ''}
                    
                    {f'<div class="section"><h3>📝 Дополнительная информация</h3><p>{additional_info}</p></div>' if additional_info else ''}
                    
                    <div class="footer">
                        <p><strong>Время отправки:</strong> {request.POST.get('timestamp', 'Не указано')}</p>
                        <p><strong>IP адрес:</strong> {request.META.get('REMOTE_ADDR', 'Не определен')}</p>
                        <p><strong>User-Agent:</strong> {request.META.get('HTTP_USER_AGENT', 'Не определен')}</p>
                    </div>
                </body>
                </html>
                """
                
                # Отправляем email администратору
                email_message = EmailMessage(
                    subject=f"Расчет сметы - {name} ({project_type_display})",
                    body=body_html,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=["mail@expertsmet.ru"],
                    reply_to=[email],
                )
                email_message.content_subtype = "html"
                email_message.send()
                
                # Отправляем подтверждение клиенту только если email валиден
                if send_to_client:
                    client_subject = "Ваш расчет сметы от Expertsmet"
                    client_message_html = f"""
                    <html>
                    <body>
                        <h2>Спасибо за обращение в Expertsmet!</h2>
                        <p>Мы получили ваш запрос на расчет сметы для проекта:</p>
                        <ul>
                            <li><strong>Тип:</strong> {project_type_display}</li>
                            <li><strong>Площадь:</strong> {area} м²</li>
                            <li><strong>Сложность:</strong> {complexity_display}</li>
                            <li><strong>Срочность:</strong> {urgency_display}</li>
                        </ul>
                        
                        <p>Наши специалисты свяжутся с вами в течение 2 часов для уточнения деталей и предоставления точного расчета.</p>
                        
                        <p>Если у вас есть срочные вопросы, звоните:</p>
                        <p>📞 <a href="tel:88003008772">8 (800) 300 87 72</a></p>
                        <p>📱 <a href="tel:+79957903777">+7 (995) 790-37-77</a> (WhatsApp, Telegram)</p>
                        
                        <br>
                        <p>С уважением,<br>Команда Expertsmet</p>
                    </body>
                    </html>
                    """
                    
                    client_email = EmailMessage(
                        subject=client_subject,
                        body=client_message_html,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                    )
                    client_email.content_subtype = "html"
                    client_email.send()
                    
                    logger.info(f"Подтверждение отправлено клиенту {email}")
                else:
                    logger.info(f"Подтверждение клиенту не отправлено (тестовый email: {email})")
                
                # Логируем успешную отправку
                logger.info(f"Расчет сметы отправлен от {name} ({email}) для проекта {project_type_display}")
                
                # Добавляем сообщение об успехе
                messages.success(request, 'Ваш запрос на расчет сметы успешно отправлен! Мы свяжемся с вами в течение 2 часов.')
                
                return redirect("thank-you")
                
            except Exception as e:
                # Логируем ошибку
                logger.error(f"Ошибка отправки расчета сметы: {e}")
                
                # Добавляем сообщение об ошибке
                messages.error(request, 'Произошла ошибка при отправке запроса. Пожалуйста, попробуйте позже или свяжитесь с нами по телефону.')
                
                return redirect("calculator")
        else:
            # Если форма невалидна, показываем ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле {field}: {error}")
    else:
        form = CalculatorForm()
    
    return render(request, 'main/calculator.html', {'form': form})

def about(request):
    return render(request, 'main/about.html')

def contacts(request):
    return render(request, 'main/contacts.html')

def robots_txt(request):
    host = request.META.get('HTTP_HOST', request.get_host())
    # Убираем порт, если есть
    if ':' in host:
        host = host.split(':', 1)[0]
    
    # Явно обрабатываем основной домен и www как основной
    if host in ("expertsmet.ru", "www.expertsmet.ru"):
        subdomain_mode = False
    else:
        # Режим поддомена корректен только если есть как минимум два уровня до TLD (len(parts) > 2)
        parts = host.split('.')
        subdomain_mode = len(parts) > 2 and not host.startswith('www.')
    
    # Если это поддомен города
    if subdomain_mode:
        subdomain = host.split('.')[0]
        
        # Определяем город по субдомену (с учетом алиасов)
        city = get_city_by_subdomain(subdomain)
        
        if city:
            # Используем содержимое из созданных файлов robots.txt
            lines = [
                "User-agent: *",
                "Allow: /",
                "",
                "# Разрешаем индексацию основных страниц",
                "Allow: /about/",
                "Allow: /services/",
                "Allow: /portfolio/",
                "Allow: /blog/",
                "Allow: /contact/",
                "",
                "# Запрещаем индексацию служебных страниц",
                "Disallow: /admin/",
                "Disallow: /static/admin/",
                "Disallow: /media/",
                "Disallow: /staticfiles/",
                "Disallow: /logs/",
                "Disallow: /venv/",
                "Disallow: /__pycache__/",
                "Disallow: /*.py$",
                "Disallow: /*.sqlite3$",
                "Disallow: /*.log$",
                "Disallow: /debug_*",
                "Disallow: /test_*",
                "",
                "# Запрещаем индексацию временных файлов",
                "Disallow: /.DS_Store",
                "Disallow: /Thumbs.db",
                "",
                "# Разрешаем индексацию изображений и CSS/JS",
                "Allow: /static/",
                "Allow: /static/main/",
                "Allow: /static/main/css/",
                "Allow: /static/main/js/",
                "Allow: /static/main/images/",
                "Allow: /static/main/img/",
                "",
                f"# Sitemap для {city['subdomain']}",
                f"Sitemap: https://{city['subdomain']}.expertsmet.ru/sitemap.xml",
                "",
                "# Crawl-delay для уважительного отношения к серверу",
                "Crawl-delay: 1"
            ]
        else:
            # Неизвестный поддомен - блокируем индексацию
            lines = [
                "User-agent: *",
                "Disallow: /",
                "",
                "# Неизвестный поддомен - индексация запрещена"
            ]
    else:
        # Основной домен expertsmet.ru
        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /city/",
            "",
            "# Разрешаем индексацию основных страниц",
            "Allow: /about/",
            "Allow: /services/",
            "Allow: /portfolio/",
            "Allow: /blog/",
            "Allow: /contact/",
            "",
            "# Запрещаем индексацию служебных страниц",
            "Disallow: /admin/",
            "Disallow: /static/admin/",
            "Disallow: /media/",
            "Disallow: /staticfiles/",
            "Disallow: /logs/",
            "Disallow: /venv/",
            "Disallow: /__pycache__/",
            "Disallow: /*.py$",
            "Disallow: /*.sqlite3$",
            "Disallow: /*.log$",
            "Disallow: /debug_*",
            "Disallow: /test_*",
            "",
            "# Запрещаем индексацию временных файлов",
            "Disallow: /.DS_Store",
            "Disallow: /Thumbs.db",
            "",
            "# Разрешаем индексацию изображений и CSS/JS",
            "Allow: /static/",
            "Allow: /static/main/",
            "Allow: /static/main/css/",
            "Allow: /static/main/js/",
            "Allow: /static/main/images/",
            "Allow: /static/main/img/",
            "",
            "# Sitemap для основного домена",
            "Sitemap: https://expertsmet.ru/sitemap.xml",
            "",
            "# Crawl-delay для уважительного отношения к серверу",
            "Crawl-delay: 1"
        ]
    
    response = HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
    # Небольшое кэширование, чтобы снизить нагрузку, но не мешать обновлениям
    response["Cache-Control"] = "public, max-age=3600"
    return response


def sitemap_view(request):
    host = request.get_host().split(':')[0]
    # Определяем, является ли запрос городским поддоменом
    parts = host.split('.') if host else []
    subdomain = parts[0] if len(parts) > 2 and not host.startswith('www.') else None
    city_data = get_city_by_subdomain(subdomain) if subdomain else None

    if city_data:
        # Генерируем sitemap для конкретного города
        return generate_city_sitemap(request, city_data)

    return django_sitemap(request, GLOBAL_SITEMAPS)


def generate_city_sitemap(request, city_data):
    """Генерирует sitemap для конкретного города"""
    from django.http import HttpResponse
    from django.utils import timezone
    
    base_url = city_data['url'].rstrip('/')
    urls = []
    
    # Добавляем статические страницы
    for item in CITY_SITEMAP_STATIC_PATHS:
        if not item:
            loc = f"{base_url}/"
        else:
            loc = f"{base_url}/{item.strip('/')}/"
        urls.append({
            'loc': loc,
            'changefreq': 'weekly',
            'priority': '0.8',
        })
    
    # Добавляем статьи
    from articles.models import Articles
    articles = Articles.objects.all().order_by('-data')
    for article in articles:
        article_url = article.get_absolute_url()
        loc = f"{base_url}{article_url}"
        lastmod = article.data.strftime('%Y-%m-%d')
        urls.append({
            'loc': loc,
            'lastmod': lastmod,
            'changefreq': 'daily',
            'priority': '0.6',
        })
    
    # Генерируем XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url_data in urls:
        xml_content += '<url>\n'
        xml_content += f'<loc>{url_data["loc"]}</loc>\n'
        if 'lastmod' in url_data:
            xml_content += f'<lastmod>{url_data["lastmod"]}</lastmod>\n'
        xml_content += f'<changefreq>{url_data["changefreq"]}</changefreq>\n'
        xml_content += f'<priority>{url_data["priority"]}</priority>\n'
        xml_content += '</url>\n'
    
    xml_content += '</urlset>'
    
    response = HttpResponse(xml_content, content_type='application/xml; charset=utf-8')
    response['Cache-Control'] = 'public, max-age=3600'
    return response


def send_form_email(request):
    if request.method == "POST":
        try:
            # Получаем данные формы
            name = request.POST.get('name', 'Не указано')
            email = request.POST.get('email', 'Не указано')
            phone = request.POST.get('phone', 'Не указано')
            message = request.POST.get('message', 'Не указано')
            
            # Создаем HTML таблицу с данными
            body_rows = ""
            form_data = {
                'Имя': name,
                'Email': email,
                'Телефон': phone,
                'Сообщение': message
            }
            
            for key, value in form_data.items():
                body_rows += (
                    f"<tr><td style='padding: 10px; border: #e9e9e9 1px solid; background-color: #f9f9f9;'>"
                    f"<strong>{key}</strong></td>"
                    f"<td style='padding: 10px; border: #e9e9e9 1px solid;'>{value}</td></tr>"
                )
            
            body_html = f"""
            <html>
            <head>
                <style>
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ padding: 10px; border: 1px solid #e9e9e9; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h2>Новая заявка с сайта Expertsmet</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Поле</th>
                            <th>Значение</th>
                        </tr>
                    </thead>
                    <tbody>
                        {body_rows}
                    </tbody>
                </table>
                <p><strong>Время отправки:</strong> {request.POST.get('timestamp', 'Не указано')}</p>
            </body>
            </html>
            """

            # Создаем email сообщение
            email_message = EmailMessage(
                subject=f"Новая заявка с сайта Expertsmet - {name}",
                body=body_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=["mail@expertsmet.ru"],
                reply_to=[email] if email != 'Не указано' else None,
            )
            email_message.content_subtype = "html"

            # Прикрепляем файлы, если они есть
            files = request.FILES.getlist("file")
            for f in files:
                try:
                    email_message.attach(f.name, f.read(), f.content_type)
                    logger.info(f"Файл {f.name} успешно прикреплен к email")
                except Exception as e:
                    logger.error(f"Ошибка прикрепления файла {f.name}: {e}")

            # Отправляем email
            email_message.send()
            
            # Логируем успешную отправку
            logger.info(f"Email успешно отправлен от {name} ({email})")
            
            # Добавляем сообщение об успехе
            messages.success(request, 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.')
            
            return redirect("thank-you")
            
        except Exception as e:
            # Логируем ошибку
            logger.error(f"Ошибка отправки email: {e}")
            
            # В режиме разработки показываем детали ошибки
            if settings.DEBUG:
                messages.error(request, f'Ошибка отправки: {str(e)}')
            else:
                messages.error(request, 'Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже или свяжитесь с нами по телефону.')
            
            return redirect("contacts")
    
    return HttpResponse("Неверный запрос", status=400)

def quick_contact(request):
    from .forms import QuickContactForm
    
    if request.method == 'POST':
        form = QuickContactForm(request.POST)
        if form.is_valid():
            try:
                # Получаем данные формы
                name = form.cleaned_data['name']
                phone = form.cleaned_data['phone']
                message = form.cleaned_data['message']
                
                # Создаем HTML email
                body_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                        .section {{ margin: 20px 0; }}
                        .field {{ margin: 10px 0; }}
                        .field-label {{ font-weight: bold; color: #495057; }}
                        .field-value {{ margin-left: 10px; }}
                        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>📞 Быстрая заявка с сайта Expertsmet</h2>
                    </div>
                    
                    <div class="section">
                        <h3>👤 Контактная информация</h3>
                        <div class="field">
                            <span class="field-label">Имя:</span>
                            <span class="field-value">{name}</span>
                        </div>
                        <div class="field">
                            <span class="field-label">Телефон:</span>
                            <span class="field-value">{phone}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>📝 Сообщение</h3>
                        <p>{message}</p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Время отправки:</strong> {request.POST.get('timestamp', 'Не указано')}</p>
                        <p><strong>IP адрес:</strong> {request.META.get('REMOTE_ADDR', 'Не определен')}</p>
                        <p><strong>Источник:</strong> Быстрая форма связи</p>
                    </div>
                </body>
                </html>
                """
                
                # Отправляем email администратору
                email_message = EmailMessage(
                    subject=f"Быстрая заявка - {name}",
                    body=body_html,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=["mail@expertsmet.ru"],
                )
                email_message.content_subtype = "html"
                email_message.send()
                
                # Логируем успешную отправку
                logger.info(f"Быстрая заявка отправлена от {name} ({phone})")
                
                # Возвращаем JSON ответ для AJAX запросов
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': True,
                        'message': 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.'
                    })
                
                # Для обычных POST запросов
                messages.success(request, 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.')
                return redirect("index")
                
            except Exception as e:
                # Логируем ошибку
                logger.error(f"Ошибка отправки быстрой заявки: {e}")
                
                # Возвращаем JSON ответ для AJAX запросов
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'message': 'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже.'
                    }, status=500)
                
                # Для обычных POST запросов
                messages.error(request, 'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже.')
                return redirect("index")
        else:
            # Если форма невалидна
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'message': 'Пожалуйста, заполните все обязательные поля корректно.',
                    'errors': form.errors
                }, status=400)
            
            # Для обычных POST запросов
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле {field}: {error}")
            return redirect("index")
    
    # Для GET запросов
    return redirect("index")

def thank_you(request):
    return render(request, "main/thank_you.html")

def health_check(request):
    """Health check endpoint for Docker containers"""
    from django.http import JsonResponse
    from django.db import connection
    import time
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': time.time(),
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': time.time(),
            'database': 'disconnected',
            'error': str(e)
        }, status=503)

def subscribe(request):
    from .forms import SubscribeForm
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            try:
                subscription = form.save()
                
                # Проверяем, что email адрес валиден и не является тестовым
                subscriber_email = subscription.email
                if not subscriber_email or 'example.com' in subscriber_email or 'test' in subscriber_email:
                    logger.warning(f"Попытка подписки с тестовым email: {subscriber_email}")
                    messages.warning(request, 'Подписка сохранена, но email подтверждение не отправлено (тестовый адрес).')
                    return redirect("index")
                
                # Отправляем email подтверждения подписчику
                subject = "Спасибо за подписку на обновления Expertsmet!"
                message_html = f"""
                <html>
                <body>
                    <h2>Добро пожаловать в команду Expertsmet!</h2>
                    <p>Вы успешно подписались на наши обновления.</p>
                    <p>Теперь вы будете получать уведомления о:</p>
                    <ul>
                        <li>Новых статьях и полезных материалах</li>
                        <li>Обновлениях в сфере сметного дела</li>
                        <li>Специальных предложениях и акциях</li>
                    </ul>
                    <p>Если у вас есть вопросы, свяжитесь с нами:</p>
                    <p>📞 <a href="tel:88003008772">8 (800) 300 87 72</a></p>
                    <p>📧 <a href="mailto:mail@expertsmet.ru">mail@expertsmet.ru</a></p>
                    <br>
                    <p>С уважением,<br>Команда Expertsmet</p>
                </body>
                </html>
                """
                
                # Отправляем email подписчику
                email_message = EmailMessage(
                    subject=subject,
                    body=message_html,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[subscriber_email],
                )
                email_message.content_subtype = "html"
                email_message.send()
                
                # Отправляем уведомление администратору
                admin_subject = f"Новая подписка на рассылку: {subscriber_email}"
                admin_message = f"Новый подписчик: {subscriber_email}\nДата подписки: {subscription.created_at}"
                
                send_mail(
                    admin_subject,
                    admin_message,
                    settings.DEFAULT_FROM_EMAIL,
                    ["mail@expertsmet.ru"]
                )
                
                logger.info(f"Новая подписка: {subscriber_email}")
                messages.success(request, 'Спасибо за подписку! Проверьте вашу почту для подтверждения.')
                
                return redirect("index")
                
            except Exception as e:
                logger.error(f"Ошибка при подписке {subscription.email if 'subscription' in locals() else 'неизвестно'}: {e}")
                
                # В режиме разработки показываем детали ошибки
                if settings.DEBUG:
                    messages.error(request, f'Ошибка отправки email: {str(e)}. Но подписка сохранена.')
                else:
                    messages.error(request, 'Произошла ошибка при отправке подтверждения. Пожалуйста, попробуйте позже.')
                
                return redirect("index")
        else:
            # Если форма невалидна, показываем ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле {field}: {error}")
            return redirect("index")
    else:
        return redirect("index")
