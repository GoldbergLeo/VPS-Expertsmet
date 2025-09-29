from django.shortcuts import render
from django.views.generic import DetailView
from django.conf import settings
from django.templatetags.static import static
from main.cities_config import get_city_by_key
from pathlib import Path
import random
from .models import Articles

def articles_home(request):
    articles = Articles.objects.order_by('data')
    return render(request, 'articles/articles_list.html', {'articles': articles})


class NewsDetailView(DetailView):
    model = Articles
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Канонический URL всегда указывает на текущий URL страницы
        request = self.request
        context['canonical_url'] = request.build_absolute_uri()
        
        image_sources = [
            (Path(settings.BASE_DIR) / 'static' / 'main' / 'img' / 'articles', 'main/img/articles', None),
            (Path(settings.BASE_DIR) / 'static' / 'main' / 'img', 'main/img', lambda name: name.lower().startswith('articles_')),
        ]
        allowed_ext = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        candidates = []

        for directory, prefix, predicate in image_sources:
            if not directory.is_dir():
                continue
            for file in directory.iterdir():
                if not file.is_file():
                    continue
                if file.suffix.lower() not in allowed_ext:
                    continue
                if predicate and not predicate(file.name):
                    continue
                candidates.append(f"{prefix}/{file.name}")

        if candidates:
            chosen = random.choice(candidates)
            context['random_image_url'] = static(chosen)
        else:
            context['random_image_url'] = Articles.get_placeholder_image_url()
        
        # Получаем последние 3 статьи, исключая текущую (чтобы не дублировать)
        context['latest_articles'] = (
            Articles.objects
            .exclude(pk=self.object.pk)
            .order_by('-data')[:3]
        )
        
        return context
