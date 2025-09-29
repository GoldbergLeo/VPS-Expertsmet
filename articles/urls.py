from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # URL для отображения списка статей с именем "articles_list"
    path('', views.articles_home, name='articles_list'),

    # Redirect for the missing article that Googlebot is requesting
    path('kak-sostavlyaetsya-smetnaya-dokumentaciya/',
         RedirectView.as_view(url='/articles/', permanent=True),
         name='redirect_missing_article'),

    # URL для детального отображения статьи, например, с использованием pk
    path('<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
]