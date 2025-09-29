from django.contrib import admin
from django.utils.html import format_html
from .models import Articles

class ArticlesAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'data', 'image', 'meta_title', 'meta_description', 'view_link')
    list_filter = ('data',)
    search_fields = ('title', 'discr', 'full_text', 'meta_keywords')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'data')
        }),
        ('Контент', {
            'fields': ('discr', 'full_text', 'image')  # Добавляем image здесь
        }),
        ('SEO настройки', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
    )

    def view_link(self, obj):
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank">Просмотр</a>', url)
    view_link.short_description = "Ссылка на страницу"

admin.site.register(Articles, ArticlesAdmin)