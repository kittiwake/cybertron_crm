#!/bin/sh

while ! nc -z postgres 5432; do
  echo "Waiting for PostgreSQL to become available..."
  sleep 1
done

# Применяем миграции
python manage.py migrate --no-input

# Собираем статические файлы
python manage.py collectstatic --no-input

# Запускаем Django-приложение с помощью Gunicorn
gunicorn cybcrm.wsgi:application --bind 0.0.0.0:8000 &

# Запускаем tg_bot
python manage.py tg_bot

# Поддерживаем работу скрипта
exec "$@"
