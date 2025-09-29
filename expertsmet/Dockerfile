# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Копируем скрипт запуска
COPY expertsmet/start.sh /app/start.sh

RUN chmod +x /app/start.sh

# Создаем необходимые директории и устанавливаем права
RUN mkdir -p /app/logs /app/staticfiles /app/media
RUN chmod 755 /app/logs /app/staticfiles /app/media

# Создаем пользователя для запуска приложения (безопасность)
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["/app/start.sh"]